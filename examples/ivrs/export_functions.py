import os
import xml.etree.ElementTree as ET
import base64
import zlib
import gzip
from io import BytesIO
import argparse
import csv

import logging

from five9 import five9_session

# Function to decompress the zipped function body
def decompress_function_body(compressed_body):
    try:
        # Attempt Base64 decoding
        decoded_data = base64.b64decode(compressed_body)
        
        # Try zlib decompression
        try:
            decompressed_data = zlib.decompress(decoded_data)
            return decompressed_data.decode('utf-8')
        except zlib.error:
            # If zlib decompression fails, try gzip
            with gzip.GzipFile(fileobj=BytesIO(decoded_data)) as gzip_file:
                decompressed_data = gzip_file.read()
                return decompressed_data.decode('utf-8')
    
    except Exception as e:
        logging.info(f"Failed to decompress function body: {e}")
        return None

# Function to extract functions from the IVR XML script and format as proper JavaScript
def extract_functions_from_ivr(xml_content):
    root = ET.fromstring(xml_content)
    functions = []
    
    # Find the <functions> element
    functions_element = root.find("functions")
    if functions_element is not None:
        for entry in functions_element.findall("entry"):
            function_name = entry.find("value/name").text.strip()
            function_body = entry.find("value/functionBody").text.strip()
            
            # Decompress the function body
            decompressed_function_body = decompress_function_body(function_body)
            if decompressed_function_body:
                # Extract function arguments
                arguments_list = []
                for argument in entry.findall("value/arguments/arguments"):
                    argument_name = argument.find("name").text.strip()
                    arguments_list.append(argument_name)
                
                # Construct the JavaScript function definition
                arguments_str = ", ".join(arguments_list)  # Join the arguments into a single string
                function_js = f"function {function_name}({arguments_str}) {{\n{decompressed_function_body}\n}}\n"
                function_details = {
                    "name": function_name,
                    "arguments": arguments_list,
                    "js": function_js
                }
                functions.append(function_details)
                
            else:
                logging.info(f"Could not decompress function: {function_name}")
    
    return functions


if __name__ == "__main__":

    # Set the folder path to the current directory where the script is running
    ivr_folder_path = os.getcwd()

    parser = argparse.ArgumentParser(description='Export IVR functions from Five9 IVR scripts')

    # Optional arguments using '--'
    parser.add_argument('--username', type=str, help='Five9 username')
    parser.add_argument('--password', type=str, help='Five9 password')
    parser.add_argument('--hostalias', type=str, default='us', help='Five9 host alias (us, ca, eu, frk, in)')

    args = parser.parse_args()
    logging.info(args)
    five9Username = args.username
    five9Password = args.password
    five9Host = args.hostalias.lower()

    # Initialize the Five9 client
    client = five9_session.Five9Client(
        five9username=five9Username,
        five9password=five9Password,
        api_hostname_alias=five9Host
    )

    ivrs = client.service.getIVRScripts()

    all_functions = []

    for script in ivrs:
        scriptxml = script['xmlDefinition']
        functions = extract_functions_from_ivr(scriptxml)

        if functions:
            # Prepare the new filename
            new_filename = f"{os.path.splitext(script['name'])[0]}_functions.js"

            subfolder = f'private/{client.domain_name}/ivr_function_exports'
            if not os.path.exists(subfolder):
                os.makedirs(subfolder)

            # Collect functions and script names for CSV
            for function in functions:
                all_functions.append({'script_name': script['name'], 'function_name': function['name']})

            # Save the functions to a new JS file
            with open(os.path.join(subfolder, f'{script["name"]}.js'), 'w', encoding='utf-8') as new_file:
                functions_str = [function['js'] for function in functions]
                new_file.write("\n".join(functions_str))
            logging.info(f"Extracted functions saved to: {new_filename}")
        else:
            logging.info(f"No functions found in: {script['name']}")

    # Sort the functions alphabetically by script name, then by function name
    all_functions_sorted = sorted(all_functions, key=lambda x: (x['script_name'], x['function_name']))

    # Write the sorted functions to the CSV file
    csv_file_path = f'{subfolder}/functions_summary.csv'
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['script_name', 'function_name'])

        # Write the header only if the file does not exist yet
        if not file_exists:
            writer.writeheader()

        # Write the rows of sorted data
        for function_data in all_functions_sorted:
            writer.writerow(function_data)

    logging.info(f"CSV summary of functions saved to: {csv_file_path}")
