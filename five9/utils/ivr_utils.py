import xml.etree.ElementTree as ET
import base64
import collections
import json
import re
import zlib
import gzip
from io import BytesIO
import logging


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
def extract_jsfunctions_from_ivr(xml_content):
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


def ivr_variable_usage(ivrs, verbose=False):
    """
    Analyzes a list of IVR (Interactive Voice Response) objects to identify the usage of script variables within them.

    Args:
    ivrs (list): A list of IVR objects (should be obtained from the getIvrScripts method).
    verbose (bool): If True, the function prints the dictionary of variables and their corresponding IVRs in JSON format. Defaults to False.

    The function scans through the 'xmlDefinition' of each IVR object looking for script variables. It ignores any IVR objects with "EXAMPLE" in their name. Each variable is then cataloged along with the IVR names where it appears.

    Returns:
    OrderedDict: A dictionary where keys are script variable names and values are lists of IVR names where these variables are used. The dictionary is sorted alphabetically by the variable names.
    """

    # Initialize an empty dictionary to store the script variables and the IVRs where they appear
    ivr_variables = {}

    # Compile a regular expression to find script variables in the xmlDefinition attribute
    script_variable_pattern = re.compile(
        r"(?<=<variableName>)(.*?)(?=<\/variableName>)"
    )

    # Iterate over the IVR objects
    for ivr in ivrs:
        # Skip IVRs with "EXAMPLE" in their name
        if "EXAMPLE" in ivr.name:
            continue

        # Find all instances of script variables in the xmlDefinition attribute
        script_variables = script_variable_pattern.finditer(ivr.xmlDefinition)

        # Iterate over the script variables
        for var in script_variables:
            # Extract the variable name
            b = var.span()[0]
            e = var.span()[1]
            variable = ivr.xmlDefinition[b:e]
            # Split the variable name into parts at the period
            variable_parts = variable.split(".")

            # If the variable has more than one part, add it to the ivr_variables dictionary
            if len(variable_parts) > 1:
                if ivr_variables.get(variable, None) == None:
                    ivr_variables[variable] = []
                if ivr.name not in ivr_variables[variable]:
                    ivr_variables[variable].append(ivr.name)

    # Sort the ivr_variables dictionary
    ivr_variables = collections.OrderedDict(sorted(ivr_variables.items()))

    # If verbose is True, print the ivr_variables dictionary as a JSON object
    if verbose == True:
        j = json.dumps(ivr_variables, indent=4)
        print(j)

    # Return the ivr_variables dictionary
    return ivr_variables

