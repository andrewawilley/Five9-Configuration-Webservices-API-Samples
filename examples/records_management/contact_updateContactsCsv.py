import argparse
import csv

from five9 import five9_session


DEFAULT_CRM_UPDATE_SETTINGS = {
    "allowDataCleanup": True,
    # 'callbackAuthProfileName': 'string',
    # 'callbackFormat': 'string',
    # 'callbackUrl': 'string',
    # 'countryCode': 'string',
    # 'failOnFieldParseError': False,
    # 'reportEmail': 'string',
    "crmAddMode": "ADD_NEW",
    "crmUpdateMode": "UPDATE_ALL",
    "separator": ",",
    "skipHeaderLine": True,
    "fieldsMapping": [
        {"columnNumber": 1, "fieldName": "number1", "key": True},
        {"columnNumber": 2, "fieldName": "outPulse", "key": False},
    ],
}


def update_contacts_from_csv(client, csv_file):
    """
    Update user details in Five9 from a CSV file.

    Args:
        client (Five9Client): The Five9 API client.
        csv_file (str): The CSV file with user details.
    """
    with open(csv_file, mode="r") as file:
        # pass the full contents of the file to the API
        update_settings = DEFAULT_CRM_UPDATE_SETTINGS
        try:
            response = client.service.updateContactsCsv(
                crmUpdateSettings=update_settings, csvData=file.read()
            )
            print(response)
        except Exception as e:
            print(e)

        print(client.latest_envelopes)    
        return
            


# if main, then run the script

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update contact record details in Five9 from a CSV file."
    )
    parser.add_argument(
        "-f",
        "--file",
        help="The CSV file with contact details.",
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Five9 Username for authentication, password argument required if provided",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Five9 Password for authentication, username argument required if provided",
        required=False,
    )

    args = parser.parse_args()
    five9_username = args.username or None
    five9_password = args.password or None

    # Get the Five9 API client
    client = five9_session.Five9Client(
        five9username=five9_username, five9password=five9_password
    )

    # Update the contacts from the CSV file
    update_contacts_from_csv(client, args.file)
