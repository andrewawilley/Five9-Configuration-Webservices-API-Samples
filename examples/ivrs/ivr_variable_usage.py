import os
import csv
import argparse
from five9.utils.ivr_utils import ivr_variable_usage
from five9 import five9_session


def write_ordered_dict_to_csv(ordered_dict, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Variable Name", "IVR Script Name"])  # Write header

        # Write each variable and its associated script name(s)
        for variable_name, script_names in ordered_dict.items():
            for script_name in script_names:
                writer.writerow([variable_name, script_name])


if __name__ == "__main__":
    # Set the folder path to the current directory where the script is running
    current_dir = os.getcwd()

    # Create the "private" directory path
    private_dir = os.path.join(current_dir, "private")

    # Ensure the "private" folder exists
    os.makedirs(private_dir, exist_ok=True)

    parser = argparse.ArgumentParser(
        description="Export IVR functions from Five9 IVR scripts"
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
    parser.add_argument("--verbose", action="store_false", help="Print verbose output")
    parser.add_argument("--outputfile", type=str, help="Output file for variable usage")

    args = parser.parse_args()
    five9Username = args.username or input("Enter your Five9 username: ")
    five9Password = args.password
    five9Host = args.hostalias.lower()

    verbose = args.verbose
    outputfile = args.outputfile or "ivr_variable_usage.csv"

    # Ensure the file is saved inside the "private" folder
    outputfile_path = os.path.join(private_dir, outputfile)

    # Initialize the Five9 client
    client = five9_session.Five9Client(
        five9username=five9Username,
        five9password=five9Password,
        api_hostname_alias=five9Host,
    )

    ivrs = client.service.getIVRScripts()

    ivr_variables = ivr_variable_usage(ivrs, verbose=True)

    # Write the variable usage to a CSV file
    write_ordered_dict_to_csv(ivr_variables, outputfile_path)

    print(f"File saved to: {outputfile_path}")
