import csv
import time
import zeep
from tqdm import tqdm
import five9_session

def update_user_federation_ids(csv_path, client=None):
    """
    Updates federation IDs of users in the Five9 domain based on a provided CSV file.

    This function reads user data from a CSV file, then updates the federation IDs 
    of corresponding users in the Five9 domain. It assumes each row in the CSV file
    contains 'userName' and 'federationId' columns.

    Parameters:
    csv_path: str
        The path to the CSV file containing the user data.
    client (optional): Zeep Client object
        The client used to interact with the Five9 domain.
        If None, a new Five9Client instance is created.

    Returns:
    tuple: (updated_users, error_users, missing_users)
        updated_users: list of user objects successfully updated.
        error_users: list of user objects where updates failed.
        missing_users: list of users in the CSV file not found in the Five9 domain.

    Raises:
    zeep.exceptions.Fault
        If an error occurs during the user update process.

    Note:
    The function assumes the CSV file has columns 'userName' and 'federationId'.
    It also assumes that user objects in the Five9 domain have a 'generalInfo' attribute.
    """

    if client is None:
        client = five9_session.Five9Client()

    # Read CSV file and populate a dictionary of usernames to lookup federationIds
    user_federation_Ids = {}

    with open(csv_path, mode="r") as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            user_federation_Ids[row["userName"]] = row["federationId"]

    users = client.service.getUsersInfo()

    users_to_update = []
    missing_users = []

    for user in users:
        if user_federation_Ids.get(user["generalInfo"]["userName"], "skip") != "skip":
            users_to_update.append(user)
        else:
            missing_users.append(user)

    updated_users = []
    error_users = []

    total_users = len(users_to_update)

    with tqdm(total=total_users, desc="Updating users", mininterval=1) as pbar:
        for user in users_to_update:
            try:
                user_federationId = user_federation_Ids.get(user["generalInfo"]["userName"], "skip")
                if user_federationId != "skip":
                    user.generalInfo.federationId = user_federationId
                    modified_user = client.service.modifyUser(user.generalInfo)
                    updated_users.append(modified_user)
                    time.sleep(0.3)
            except zeep.exceptions.Fault as e:
                error_users.append(user)
            finally:
                pbar.update(1)
                pbar.set_postfix({"Updated": len(updated_users), "Errors": len(error_users)})

    return updated_users, error_users, missing_users
