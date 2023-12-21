import five9_session
from util import get_random_password
from tqdm import tqdm


def bulk_create_users(client, user_data, template_agent_username):
    """
    Bulk creates user accounts in the Five9 domain based on provided user data and a template agent.

    This function creates new user accounts using the specified template agent's roles and skills.
    Each user in the `user_data` list is created with unique credentials and the same roles and skills
    as the template agent.

    Parameters:
    client: Zeep Client object
        The client used to interact with the Five9 domain.
    user_data: list of dicts
        A list of dictionaries, each representing a user to be created.
        Each dictionary should contain keys: 'userName', 'password', 'firstName', 'lastName', 'EMail'.
    template_agent_username: str
        The username of the template agent whose roles and skills will be copied.

    Returns:
    list:
        A list of successfully created user objects.

    Raises:
    Exception
        If an error occurs during the user creation process.
    """

    # Fetch template agent details
    template_agent = client.service.getUserInfo(template_agent_username)
    roles = template_agent.roles
    skills = template_agent.skills

    created_users = []

    with tqdm(total=len(user_data), desc="Creating users", mininterval=1) as pbar:
        for user in user_data:
            try:
                # Assign template agent skills to new user
                skills[0].userName = user["userName"]
                new_user = client.service.createUser({"generalInfo": user})
                created_users.append(new_user)
            except Exception as e:
                print(f"\nFAILED to create user '{user['userName']}': {e}\n")
            finally:
                pbar.update(1)
                pbar.set_postfix({"Created": len(created_users)})

    return created_users
