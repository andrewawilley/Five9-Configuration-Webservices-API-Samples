import csv
import time

import five9_session
from tqdm import tqdm
import zeep


client = five9_session.Five9Client()
# Read CSV file and populate a dictionary of usernames to lookup federationIds
user_federation_Ids = {}

with open("users_to_update.csv", mode="r") as csvfile:
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


errors = 0
processed = 0
updated = 0

total_users = len(users_to_update)
error_users = []

# create a tqdm progress bar
with tqdm(total=total_users, desc="Updating users", mininterval=1) as pbar:
    for user in users_to_update[processed:]:
        try:
            user_federationId = user_federation_Ids.get(user["generalInfo"]["userName"], "skip")
            if user_federationId != "skip":
                user.generalInfo.federationId = user_federationId
                modified_user = client.service.modifyUser(user.generalInfo)
                updated += 1
                time.sleep(0.3)
        
        except zeep.exceptions.Fault as e:
            errors += 1
            error_users.append(user)
        
        processed += 1
        t = pbar.update(1)
        pbar.set_postfix({"Updated": updated, "Errors": errors, "Processed": processed})
