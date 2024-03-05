import time
import zeep
from tqdm import tqdm

from five9 import five9_session


def manage_user_skills(client, users_to_update, skills_to_add, skills_to_remove):
    """
    Manages skills for specified users in the Five9 domain.

    This function updates the skills of specified users by adding and removing skills
    based on provided lists. It uses the Five9 domain's service to make these updates.

    Parameters:
    client: Zeep Client object
        The client used to interact with the Five9 domain.
    users_to_update: list of str
        List of usernames for which skills will be managed.
    skills_to_add: list of str
        Skill names to be added to the users.
    skills_to_remove: list of str
        Skill names to be removed from the users.

    Returns:
    tuple: (updated_count, error_count)
        updated_count: The number of successful updates.
        error_count: The number of errors encountered during updates.

    Raises:
    zeep.exceptions.Fault
        If an error occurs during the skill management process.
    """

    skills_add_objs = []
    skills_remove_objs = []

    for skill_name in skills_to_add:
        try:
            skills_add_objs.append(client.service.getSkill(skill_name))
        except zeep.exceptions.Fault as e:
            print(f"Error retrieving skill '{skill_name}': {e}")

    for skill_name in skills_to_remove:
        try:
            skills_remove_objs.append(client.service.getSkill(skill_name))
        except zeep.exceptions.Fault as e:
            print(f"Error retrieving skill '{skill_name}': {e}")

    error_count = 0
    updated_count = 0

    with tqdm(
        total=len(users_to_update), desc="Updating user skills", mininterval=1
    ) as pbar:
        for user in users_to_update:
            try:
                for skill in skills_add_objs:
                    user_skill = {
                        "id": skill.id,
                        "level": 1,  # Assuming the highest level
                        "skillName": skill.name,
                        "userName": user,
                    }
                    client.service.userSkillAdd(userSkill=user_skill)
                    time.sleep(0.5)  # Delay to avoid rate limits

                for skill in skills_remove_objs:
                    user_skill = {
                        "id": skill.id,
                        "level": 1,
                        "skillName": skill.name,
                        "userName": user,
                    }
                    client.service.userSkillRemove(userSkill=user_skill)
                    time.sleep(0.5)  # Delay to avoid rate limits

                updated_count += 1
            except zeep.exceptions.Fault as e:
                error_count += 1
                print(f"Error updating skills for user '{user}': {e}")
            finally:
                pbar.update(1)
                pbar.set_postfix({"Updated": updated_count, "Errors": error_count})

    return updated_count, error_count
