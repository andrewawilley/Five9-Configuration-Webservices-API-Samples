import argparse
import csv

from five9 import five9_session


DEFAULT_CRM_UPDATE_SETTINGS = {
    "allowDataCleanup": True,
    "failOnFieldParseError": True,
    # 'callbackAuthProfileName': 'string',
    # 'callbackFormat': 'string',
    # 'callbackUrl': 'string',
    # 'countryCode': 'string',
    # 'reportEmail': 'string',
    "crmUpdateMode": "UPDATE_FIRST",
    "crmAddMode": "DONT_ADD",
    "separator": ",",
    "skipHeaderLine": True,
    "fieldsMapping": [
        {"columnNumber": 1, "fieldName": "number1", "key": False},
        {"columnNumber": 2, "fieldName": "uuid", "key": True},
        {"columnNumber": 2, "fieldName": "email", "key": False},
    ],
}


def update_contacts_from_csv(client, import_data):
    """
    Update user details in Five9 from a CSV file.

    Args:
        client (Five9Client): The Five9 API client.
        csv_file (str): The CSV file with user details.
    """
    update_settings = DEFAULT_CRM_UPDATE_SETTINGS
    try:
        response = client.service.asyncUpdateCrmRecords(
            crmUpdateSettings=update_settings,
            importData=import_data,
        )
        print(response)
    except Exception as e:
        print(e)

    print(client.latest_envelopes)


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

    parser.add_argument(
        "--hostalias",
        type=str,
        default="us",
        help="Five9 host alias (us, ca, eu, frk, in)",
    )

    args = parser.parse_args()
    five9_username = args.username or None
    five9_password = args.password or None

    import_data = {
        "values": {"item": ["9135554444", "abcd123456789", "anrew@livingston.com"]}
    }

    # Get the Five9 API client
    client = five9_session.Five9Client(
        five9username=five9_username, five9password=five9_password, api_hostname_alias=args.hostalias
    )

    # Update the contacts from the CSV file
    update_contacts_from_csv(client, import_data)
