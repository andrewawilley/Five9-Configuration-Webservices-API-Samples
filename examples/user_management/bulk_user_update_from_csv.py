import argparse
import csv
from datetime import datetime

import tqdm

from five9.utils.general import datatype_conversion
from five9 import five9_session


def update_user_details(
    client: five9_session.Five9Client,
    target_filename: str = "users.csv",
    simulation_mode: bool = True,
):
    """Retrieve user general info from a csv file and update the Five9 user object in VCC

    Args:
        client (five9_session.Five9Client): A Five9 client object that is authenticated and connected.
        target_filename (str, optional): A string specifying the name of the CSV file to save the user details to. Defaults to "users.csv".

    Returns:
        None: This function does not return anything, but it updates users in Five9 if any of the target values differ from what's in VCC.
    """

    # Get the user general information from the Five9 API
    vcc_users = client.service.getUsersGeneralInfo()

    # get allowed fields from the properties of first user object in the list
    allowed_fields = dir(vcc_users[0])

    users_from_csv = {}
    users_to_update = []

    update_errors = []

    # open the csv file
    with open(target_filename, "r") as file:
        reader = csv.DictReader(
            file,
            quotechar='"',
            delimiter=",",
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True,
        )
        # identify the headers in the csv file
        headers = reader.fieldnames
        # if the headers in the csv file are not in the allowed fields, exit with exception
        if not set(headers).issubset(set(allowed_fields)):
            disallowed_fields = set(headers) - set(allowed_fields)
            allowed_fields_string = "\n\t".join(allowed_fields)

            disallowed_fields_string = ", ".join(sorted(disallowed_fields))

            raise Exception(
                f"These headers in the csv file:\n\t{disallowed_fields_string}\n\nare not in the allowed fields list:\n\t{allowed_fields_string}"
            )

        # loop through each row in the csv file, add to the users_from_csv dictionary with the userName as the key
        # each row is a dictionary with the header as the key and the value as the value
        for row in reader:
            users_from_csv[row["userName"]] = row

    print("\nChecking for fields to update")
    for vcc_user in vcc_users:
        try:
            target_user = users_from_csv.get(vcc_user.userName, None)
            user_needs_update = False
            if target_user is not None:
                # for each property in the target_user, compare to the values in the user object
                # if the values are different, update the user object with the value from the target_user
                for target_field_name, target_field_value in target_user.items():
                    # get the datatype of the vcc_user[target_field_name]
                    datatype = type(vcc_user[target_field_name])
                    # convert the target_field_value to the datatype of the vcc_user[target_field_name]
                    target_field_value = datatype_conversion(
                        datatype, target_field_value
                    )

                    if target_field_value != vcc_user[target_field_name]:
                        if simulation_mode == True:
                            print(
                                f'\t{vcc_user.userName}: {target_field_name} = "{target_field_value}"'
                            )
                        vcc_user[target_field_name] = target_field_value
                        user_needs_update = True

                if user_needs_update:
                    # update the user object in Five9
                    users_to_update.append(vcc_user)

        except Exception as e:
            update_errors.append((vcc_user, e))

    print(f"\n               Total domain users: {len(vcc_users)}")
    print(f"Total users with fields to update: {len(users_to_update)}\n")

    # update the users in Five9
    if len(users_to_update) > 0:
        for user in tqdm.tqdm(users_to_update):
            try:
                if simulation_mode == False:
                    client.service.modifyUser(user)
            except Exception as e:
                update_errors.append((user, e))
    print("\n")

    if len(update_errors) > 0:
        print(f"\nErrors updating users:")
        for user, error in update_errors:
            print(f"{user.userName}: {error}")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        error_filename = f"private/update_user_errors_{timestamp}.txt"
        print(f"\nWriting errors to {error_filename}\n")
        with open(error_filename, "w") as file:
            for user, error in update_errors:
                file.write(f"{user.userName}: {error}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Takes a CSV file with user details and updates the users in Five9.\n
        It will only update users who have field values that differ from the values in Five9.\n
        If no filename is provided, it will default to private/users_to_update.csv\n
        The CSV file must have a header row with fields that match the user object properties in Five9 as documented in the Five9 API documentation.
        active
        canChangePassword
        EMail
        extension
        federationId
        firstName
        fullName
        id
        IEXScheduled
        lastName
        locale
        mediaTypeConfig
        mustChangePassword
        password
        phoneNumber
        startDate
        unifiedCommunicationId
        userName
        userProfileName

        """
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
        "-a",
        "--account",
        help="Alias for credential stored in private/credentials",
        required=False,
    )
    parser.add_argument(
        "-fn", "--filename", help="Target CSV file with path", required=False
    )
    parser.add_argument(
        "-s",
        "--simulationmode",
        help="Simulation mode goes through the motions but doesn't update VCC.  Defaults to False",
        required=False,
    )
    args = vars(parser.parse_args())

    five9_username = args["username"] or None
    five9_password = args["password"] or None
    five9_account = args["account"] or None

    simulation_mode = datatype_conversion(bool, args["simulationmode"] or "false")

    if simulation_mode == True:
        print(f"\nSIMULATION MODE\n")

    # Set the target filename to private/users_{yyyy-mm-dd}.csv
    target_filename = args["filename"] or f"private/users_to_update.csv"

    # Get the Five9 API client
    client = five9_session.Five9Client(
        five9username=five9_username,
        five9password=five9_password,
        account=five9_account,
    )

    update_user_details(
        client, target_filename=target_filename, simulation_mode=simulation_mode
    )
