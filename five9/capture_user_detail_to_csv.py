import argparse
import csv
from datetime import datetime

import five9_session


def capture_user_details(
    client: five9_session.Five9Client,
    target_generalInfo_fields: list = ["userName", "EMail", "fullName", "active"],
    target_permissions: dict = {},
    target_filename: str = "users.csv",
):
    """Retrieve user details from a Five9 client object and save them to a CSV file.

    Args:
        client (five9_session.Five9Client): A Five9 client object that is authenticated and connected.
        target_generalInfo_fields (list, optional): A list of strings specifying the general information fields to include in the CSV file. Defaults to ["userName", "EMail", "fullName", "active"].
        target_permissions (dict, optional): A dictionary specifying the role keys and permission types to include in the CSV file. The keys of the dictionary should correspond to role keys, and the values should be lists of permission types. If a user has a role with a matching key, and that role has a permission with a matching type, the value of that permission will be included in the CSV file. Defaults to {}.
        target_filename (str, optional): A string specifying the name of the CSV file to save the user details to. Defaults to "users.csv".

    Returns:
        None: This function does not return anything, but it writes the user details to a CSV file.
    """

    # Get the user information from the Five9 API
    users = client.service.getUsersInfo()

    # Create an empty list to store the agent information
    ap = []

    # Loop through each user
    for user in users:
        user_output = {}
        for attribute in target_generalInfo_fields:
            user_output[attribute] = user.generalInfo[attribute]

        for role_key in target_permissions.keys():
            if user.roles[role_key] is not None:
                for perm in user.roles[role_key]["permissions"]:
                    if perm.type in target_permissions[role_key]:
                        user_output[perm.type] = perm.value

        # Append the agent dictionary to the ap list
        ap.append(user_output)

    # Write the list of agent information to a CSV file
    with open(target_filename, "w", newline="") as file:
        # Create a CSV writer object
        writer = csv.DictWriter(file, fieldnames=ap[0].keys())

        # Write the header row
        writer.writeheader()

        # Write each dictionary as a row in the CSV file
        for row in ap:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="captures specified user details and permissions and writes the output to a csv"
    )
    parser.add_argument(
        "-u", "--username", help="Five9 Username for authentication", required=False
    )
    parser.add_argument(
        "-p", "--password", help="Five9 Password for authentication", required=False
    )
    parser.add_argument(
        "-a",
        "--account",
        help="Alias for credential stored in private/credentials",
        required=False,
    )
    parser.add_argument(
        "-fn", "--filename", help="Target Five9 Report Folder", required=False
    )
    args = vars(parser.parse_args())

    five9_username = args["username"] or None
    five9_password = args["password"] or None
    five9_account = args["account"] or None

    # Set the target filename to private/users_{yyyy-mm-dd}.csv
    target_filename = (
        args["filename"] or f"private/users_{datetime.now().strftime('%Y-%m-%d')}.csv"
    )

    # Get the Five9 API client
    client = five9_session.Five9Client(
        five9username=five9_username,
        five9password=five9_password,
        account=five9_account,
    )

    # Specify the general user fields to include in the CSV file
    target_generalInfo_fields = ["firstName", "lastName", "EMail", "active"]

    # Specify any role keys and permission types to include in the CSV file
    # target_permissions = {"agent": ["ManageAvailabilityBySkill", "CallForwarding"]}
    target_permissions = {"agent": ["ManageAvailabilityBySkill"]}

    capture_user_details(
        client,
        target_permissions=target_permissions,
        target_generalInfo_fields=target_generalInfo_fields,
        target_filename=target_filename,
    )
