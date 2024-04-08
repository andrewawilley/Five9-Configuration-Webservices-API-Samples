import argparse

from five9 import five9_session

client = five9_session.Five9Client()



def update_contacts_from_csv(client, csv_file):
    """
    Update user details in Five9 from a CSV file.

    Args:
        csv_file (str): The CSV file with user details.
    """
    pass
    


# if main, then run the script  

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update user details in Five9 from a CSV file.")
    parser.add_argument("csv_file", type=str, help="The CSV file with user details.")
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
    client = five9_session.Five9Client(five9username=five9_username, five9password=five9_password)

