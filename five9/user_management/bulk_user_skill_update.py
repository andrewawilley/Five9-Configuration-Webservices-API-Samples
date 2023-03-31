import csv
import datetime
import time

import zeep

import five9_session


client = five9_session.Five9Client()

# populate a list of usernames to manage the skills for
users_to_update = [
    "testguy3@aw_tam",
]

# populate a list of skills to add, and another list of skills to remove
skill_names_to_add = ["outbound_test", "outreach_en"]

skill_names_to_remove = ["test"]

skills_to_add = []
skills_to_remove = []

for skill in skill_names_to_add:
    try:
        skills_to_add.append(client.service.getSkill(skill))
    except zeep.exceptions.Fault as e:
        print(f"{e}")

for skill in skill_names_to_remove:
    try:
        skills_to_remove.append(client.service.getSkill(skill))
    except zeep.exceptions.Fault as e:
        print(f"{e}")


errors = 0
updated = 0

target_updates = len(users_to_update)


for user_to_update in users_to_update[updated:]:
    for target_skill_to_add in skills_to_add:
        user_skill_to_add = {
            "id": target_skill_to_add.id,
            # this could be set dynamically, hardcoded in this example to the highest level (1)
            "level": 1,
            "skillName": target_skill_to_add.name,
            "userName": user_to_update,
        }

        try:
            skill_added = client.service.userSkillAdd(userSkill=user_skill_to_add)
            # force half second delay to avoid rate limits
            time.sleep(0.5)
        except zeep.exceptions.Fault as e:
            print(f"{e}")

    for target_skill_to_remove in skills_to_remove:
        user_skill_to_remove = {
            "id": target_skill_to_remove.id,
            "skillName": target_skill_to_remove.name,
            "level": 1,
            "userName": user_to_update,
        }

        try:
            skill_removed = client.service.userSkillRemove(
                userSkill=user_skill_to_remove
            )
            # force half second delay to avoid rate limits
            time.sleep(0.5)
        except zeep.exceptions.Fault as e:
            print(f"{e}")

    updated += 1
    print(f"Updated:\t{updated}/{target_updates} \tErrors: {errors}", end="\r")
    time.sleep(0.5)

print(f"Updated:\t{updated}/{target_updates} \tErrors: {errors}")
