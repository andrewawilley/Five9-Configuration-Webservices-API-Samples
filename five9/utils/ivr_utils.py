import xml.etree.ElementTree as ET
import base64
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
