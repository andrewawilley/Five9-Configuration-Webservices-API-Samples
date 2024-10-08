import os
import argparse
import csv
import logging
import jsbeautifier
import difflib  # Import difflib for comparison
from five9 import five9_session
from five9.utils.ivr_utils import extract_jsfunctions_from_ivr

if __name__ == "__main__":

    # Set the folder path to the current directory where the script is running
    ivr_folder_path = os.getcwd()

    parser = argparse.ArgumentParser(
        description="Export IVR functions from Five9 IVR scripts and detect differences"
    )

    # Optional arguments using '--'
    parser.add_argument("--username", type=str, help="Five9 username")
    parser.add_argument("--password", type=str, help="Five9 password")
    parser.add_argument(
        "--hostalias",
        type=str,
        default="us",
        help="Five9 host alias (us, ca, eu, frk, in)",
    )

    args = parser.parse_args()
    logging.info(args)
    five9Username = args.username or input("Enter your Five9 username: ")
    five9Password = args.password
    five9Host = args.hostalias.lower()

    # Initialize the Five9 client
    client = five9_session.Five9Client(
        five9username=five9Username,
        five9password=five9Password,
        api_hostname_alias=five9Host,
    )

    ivrs = client.service.getIVRScripts()

    all_functions = {}
    beautifier_options = jsbeautifier.default_options()
    beautifier_options.indent_size = 4  # Set indentation level

    # Subfolder for storing files
    subfolder = f"private/{client.domain_name}/ivr_function_exports"
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    # Store differences in functions
    differences_log = os.path.join(subfolder, "function_differences.diff")

    with open(differences_log, "w") as diff_file:
        for script in ivrs:
            scriptxml = script["xmlDefinition"]
            functions = extract_jsfunctions_from_ivr(scriptxml)

            if functions:
                # Prepare new filename for the current script's JS functions
                new_filename = f"{os.path.splitext(script['name'])[0]}_functions.js"

                with open(
                    os.path.join(subfolder, f'{script["name"]}.js'), "w", encoding="utf-8"
                ) as new_file:
                    functions_str = [function["js"] for function in functions]
                    formatted_js = [jsbeautifier.beautify(f, beautifier_options) for f in functions_str]
                    new_file.write("\n".join(formatted_js))

                for function in functions:
                    function_name = function["name"]
                    function_js = jsbeautifier.beautify(function["js"], beautifier_options)

                    # Check if the function already exists in another script
                    if function_name in all_functions:
                        existing_function = all_functions[function_name]
                        existing_js = existing_function["js"]

                        if existing_js != function_js:
                            # Log the difference
                            diff_file.write(f"Difference found in function '{function_name}'\n")
                            diff_file.write(f"Script 1: {existing_function['script_name']}\n")
                            diff_file.write(f"Script 2: {script['name']}\n")

                            # Compare the two versions of the function
                            diff = difflib.unified_diff(
                                existing_js.splitlines(), function_js.splitlines(), lineterm=""
                            )
                            diff_file.write("\n".join(list(diff)) + "\n\n")
                            
                            logging.info(f"Difference found in function '{function_name}' between scripts.")

                    # Store the function if it's new or after comparison
                    all_functions[function_name] = {
                        "script_name": script["name"],
                        "js": function_js,
                    }

            else:
                logging.info(f"No functions found in: {script['name']}")

    logging.info(f"Differences log saved to: {differences_log}")

    # Sort the functions alphabetically by script name, then by function name
    all_functions_sorted = sorted(
        all_functions.items(), key=lambda x: (x[1]["script_name"], x[0])
    )

    # Write the sorted functions to the CSV file
    csv_file_path = f"{subfolder}/functions_summary.csv"
    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["script_name", "function_name"])

        # Write the header only if the file does not exist yet
        if not file_exists:
            writer.writeheader()

        # Write the rows of sorted data
        for function_name, function_data in all_functions_sorted:
            writer.writerow(
                {"script_name": function_data["script_name"], "function_name": function_name}
            )

    logging.info(f"CSV summary of functions saved to: {csv_file_path}")
