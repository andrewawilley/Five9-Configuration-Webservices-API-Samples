import os

import argparse
import csv

import logging

from five9 import five9_session
from five9.utils.ivr_utils import extract_jsfunctions_from_ivr


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
    five9Username = args.username or input("Enter your Five9 username: ")
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
        functions = extract_jsfunctions_from_ivr(scriptxml)

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
