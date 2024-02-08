import time

from tqdm import tqdm
import zeep

# from five9 import five9_session
from five9.util import get_random_password


def pseudo_enforce_SSO(
    client,
    users_to_update=None,
    roles_to_exclude=["admin", "supervisor"],
    safe_mode=True,
):
    """
    Updates user accounts in the Five9 domain to pseudo-enforce Single Sign-On (SSO) compliance.

    This function targets users who have a federationId but do not hold roles specified in `roles_to_exclude`.
    It sets their password to a random string and disables password change capabilities.

    Parameters:
    client: Five9 Client object
        The client used to interact with the Five9 domain.
    users_to_update (optional): list
        A list of user objects (usersInfo datatype) to update.
        If None, fetches all users from the Five9 domain.
    roles_to_exclude (optional): list of str
        Roles to be excluded from the update. Default is ["admin", "supervisor"].
        This parameter is considered only if `users_to_update` is None.
    safe_mode (optional): bool
        If True, performs updates without modifying the user data on the server.
        Useful for dry runs. Default is True.

    Returns:
    tuple: (modified_users, error_users)
        modified_users: list of user objects successfully updated.
        error_users: list of user objects where updates failed.

    Raises:
    zeep.exceptions.Fault
        If an error occurs during the update process.

    Note:
    The function assumes that user objects have attributes like `roles`, `generalInfo`, etc.,
    as per Five9 domain's structure.
    """

    if users_to_update == None:
        print("Fetching users from Five9...")
        users = client.service.getUsersInfo()

    users_to_update = []
    missing_users = []

    for user in users:
        exclude = False
        for role in roles_to_exclude:
            if user.roles[role] != None:
                exclude = True

        if exclude == False and user.generalInfo.federationId != None:
            users_to_update.append(user)
        else:
            missing_users.append(user)

    errors = 0
    processed = 0
    updated = 0

    total_users = len(users_to_update)
    error_users = []
    modified_users = []

    for user in users_to_update:
        print(f"{user.generalInfo.userName}\t{user.generalInfo.federationId}")

    # create a tqdm progress bar
    with tqdm(total=total_users, desc="Updating users", mininterval=1) as pbar:
        for user in users_to_update[processed:]:
            try:
                user.generalInfo.password = get_random_password()
                user.generalInfo.canChangePassword = False
                user.generalInfo.mustChangePassword = False
                if not safe_mode:
                    modified_user = client.service.modifyUser(user.generalInfo)
                    time.sleep(0.3)
                    modified_users.append(modified_user)
                updated += 1

            except zeep.exceptions.Fault as e:
                errors += 1
                error_users.append(user)
                print(f"Error updating {user.generalInfo.userName}: {e}")

            processed += 1
            t = pbar.update(1)
            pbar.set_postfix(
                {"Updated": updated, "Errors": errors, "Processed": processed}
            )

    return modified_users, error_users
