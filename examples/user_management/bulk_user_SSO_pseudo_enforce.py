import argparse
import csv
import logging
import os
import re
import time
from getpass import getpass

from tqdm import tqdm
import zeep

from five9.five9_session import Five9Client
from five9.utils.general import get_random_password


def append_to_csv(filename, data):
    """
    Appends data to a CSV file.

    Parameters:
    filename (str): The name of the CSV file.
    data (dict): A dictionary containing the data.
    fieldnames (list): A list of field names for the CSV file.
    """
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, data)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def read_usernames_from_csv(csv_file, username_column_header="userName"):
    """
    Reads a CSV file and extracts the list of usernames from the specified column.

    Parameters:
    csv_file (str): The path to the CSV file containing user data.
    username_column_header (str): The column header to extract usernames from. Default is 'userName'.

    Returns:
    list: A list of usernames.
    """
    usernames = []
    try:
        with open(csv_file, mode="r", encoding="utf-8-sig") as file:
            logging.info("Reading usernames from CSV file...")
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            logging.info(f"CSV file headers: {headers}")
            for row in reader:
                if username_column_header in row:
                    usernames.append(row[username_column_header])
                else:
                    logging.error(f"Column '{username_column_header}' not found in the CSV file.")
                    break
    except FileNotFoundError:
        logging.error(f"File {csv_file} not found.")
    except Exception as e:
        logging.error(f"Error reading the CSV file: {e}")
    
    logging.info(f"Read {len(usernames)} usernames from the CSV file.")

    return usernames



def should_exclude_user(user_name, exclude_usernames, exclude_patterns):
    """
    Determines if a user should be excluded based on a list of usernames and patterns.

    Parameters:
    user_name (str): The username to check.
    exclude_usernames (list): A list of specific usernames to exclude.
    exclude_patterns (list): A list of patterns (e.g., domains) to exclude.

    Returns:
    bool: True if the user should be excluded, False otherwise.
    """
    # Check if the user is in the exclude_usernames list
    if user_name in exclude_usernames:
        return True
    
    # Check if the user matches any of the patterns in exclude_patterns
    for pattern in exclude_patterns:
        if re.search(pattern, user_name):
            return True
    
    return False


def pseudo_enforce_SSO(
    client,
    usernames_to_update=None,
    exclude_usernames=None,
    exclude_patterns=None,
    roles_to_exclude=["admin", "supervisor"],
    exclude_blank_federationId=True,
    safe_mode=True,
    simulated_delay=0,
    temp_email="tempemail@temp.com",
):
    """
    Updates user accounts in the Five9 domain to pseudo-enforce Single Sign-On (SSO) compliance.

    This function targets users who have a federationId but do not hold roles specified in `roles_to_exclude`.
    It sets their password to a random string and disables password change capabilities.

    Parameters:
    client: Five9 Client object
        The client used to interact with the Five9 domain.
    usernames_to_update (optional): list
        A list of usernames to update.
    exclude_usernames (optional): list
        A list of specific usernames to exclude from updates.
    exclude_patterns (optional): list
        A list of patterns (e.g., domains) to exclude from updates.
    roles_to_exclude (optional): list of str
        Roles to be excluded from the update. Default is ["admin", "supervisor"].
    safe_mode (optional): bool
        If True, performs updates without modifying the user data on the server.
        Useful for dry runs. Default is True.
    temp_email (optional): str
        Temporary email address to set during the update. Default is "five9-password-reset@somecompany.com".

    Returns:
    tuple: (modified_users, error_users)
        modified_users: list of user objects successfully updated.
        error_users: list of user objects where updates failed.
    """

    logging.debug(f"There are {len(usernames_to_update)} users in the list of target users.")

    print("Fetching users from Five9...")
    user_fetch_start_time = time.time()
    users = client.service.getUsersInfo()
    user_fetch_end_time = time.time()
    user_fetch_time = user_fetch_end_time - user_fetch_start_time
    logging.debug(f"Fetched {len(users)} users from Five9 in {user_fetch_time:.2f} seconds.")

    users_to_update = []
    missing_users = []


    for user in users:
        user_name = user.generalInfo.userName

        # Check if user should be excluded
        if should_exclude_user(user_name, exclude_usernames, exclude_patterns):
            logging.debug(f"Excluding user: {user_name}")
            continue

        if (
            usernames_to_update is not None
        ):
            if user_name in usernames_to_update:
                users_to_update.append(user)
            continue
        
        logging.debug(f"This user snuck through: {user_name}")

        exclude = False
        for role in roles_to_exclude:
            if user.roles[role] is not None:
                exclude = True

        if not exclude and (
            user.generalInfo.federationId is not None or not exclude_blank_federationId
        ):
            users_to_update.append(user)
        else:
            missing_users.append(user)

    errors = 0
    processed = 0
    updated = 0

    total_users = len(users_to_update)
    error_users = []
    modified_users = []

    # create a tqdm progress bar
    with tqdm(total=total_users, desc="Updating users", mininterval=1) as pbar:
        filename_prefix = "" if not safe_mode else "dry_run_"
        logging.info(f"Updating {total_users} users...\n")
        for user in users_to_update[processed:]:
            try:
                original_email = user.generalInfo.EMail.strip()

                if not safe_mode:
                    user.generalInfo.EMail = temp_email
                    modified_user = client.service.modifyUser(user.generalInfo)

                    user.generalInfo.password = get_random_password()
                    user.generalInfo.canChangePassword = False
                    user.generalInfo.mustChangePassword = False

                    modified_user = client.service.modifyUser(user.generalInfo)
                    time.sleep(0.15)

                    modified_user.generalInfo.EMail = original_email
                    modified_user = client.service.modifyUser(modified_user.generalInfo)

                    modified_user_data = {
                        "userName": modified_user.generalInfo.userName,
                        "federationId": modified_user.generalInfo.federationId,
                        "email": modified_user.generalInfo.EMail,
                        "userProfilename": modified_user.generalInfo.userProfileName,
                    }
                    modified_users.append(modified_user_data)
                updated += 1

                if safe_mode == True:
                    time.sleep(simulated_delay)
                    modified_user_data = user
                write_data = {
                    "userName": user.generalInfo.userName,
                }
                append_to_csv(f"{filename_prefix}modified_users.csv", write_data)

            except zeep.exceptions.Fault as e:
                error_user_data = {
                    "userName": user.generalInfo.userName,
                    "federationId": user.generalInfo.federationId,
                    "error": str(e),
                }
                append_to_csv(f"{filename_prefix}error_users.csv", error_user_data)
                error_users.append(error_user_data)
                errors += 1
                print(f"Error updating {user.generalInfo.userName}: {e}")

            processed += 1
            pbar.update(1)
            pbar.set_postfix(
                {"Updated": updated, "Errors": errors, "Processed": processed}
            )

    return modified_users, error_users


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Update user accounts in the Five9 domain to pseudo-enforce Single Sign-On (SSO) compliance"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--username", type=str, required=True, help="Five9 username")
    parser.add_argument(
        "--password", type=str, required=False, default=None, help="Five9 password"
    )
    parser.add_argument("--safe_mode", type=int, help="Dry run mode")
    parser.add_argument(
        "--exclude_blank_federationId",
        type=int,
        required=False,
        default=True,
        help="Exclude users with blank federationId",
    )
    parser.add_argument(
        "--temp_email",
        type=str,
        default="five9-password-reset@somecompany.com",
        help="Temporary email address",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        "--simulated_delay",
        type=int,
        default=0,
        help="Simulated delay in seconds between requests (default: 0)",
    )

    parser.add_argument(
        "--hostalias",
        type=str,
        default="us",
        help="Five9 host alias (us, ca, eu, frk, in)",
    )
    
    parser.add_argument(
        "--csv_file",
        type=str,
        help="Path to the CSV file containing the list of users to update"
    )

    parser.add_argument(
        "--exclude_usernames",
        type=str,
        help="Comma-separated list of specific usernames to exclude",
    )
    
    parser.add_argument(
        "--exclude_patterns",
        type=str,
        help="Comma-separated list of patterns (e.g., domains) to exclude",
    )

    args = parser.parse_args()

    # Set logging level
    logging.basicConfig(level=args.log_level)

    password = args.password
    safe_mode = bool(int(args.safe_mode))
    temp_email = args.temp_email
    exclude_blank_federationId = bool(int(args.exclude_blank_federationId))

    if password is None:
        password = getpass()

    client = Five9Client(
        five9username=args.username,
        five9password=password,
        api_hostname_alias=args.hostalias,
    )

    usernames_to_update = None
    if args.csv_file:
        logging.info(f"Reading usernames from CSV file: {args.csv_file}")
        usernames_to_update = read_usernames_from_csv(args.csv_file)
        logging.info(f"Found {len(usernames_to_update)} usernames in the CSV file.")

    exclude_usernames = []
    if args.exclude_usernames:
        exclude_usernames = args.exclude_usernames.split(",")

    exclude_patterns = []
    if args.exclude_patterns:
        exclude_patterns = args.exclude_patterns.split(",")

    modified_users, error_users = pseudo_enforce_SSO(
        client,
        usernames_to_update=usernames_to_update,
        exclude_usernames=exclude_usernames,
        exclude_patterns=exclude_patterns,
        exclude_blank_federationId=args.exclude_blank_federationId,
        temp_email=temp_email,
        safe_mode=safe_mode,
        simulated_delay=args.simulated_delay,
    )
