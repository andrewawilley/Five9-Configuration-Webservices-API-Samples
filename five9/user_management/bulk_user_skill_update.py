import csv
import datetime
import time

import five9_session


client = five9_session.get_client()


# add in all the username/password combos with the required fields below
# here's an example of an excel formula used in one of the bulk user requests to generate a formatted user object
# ="{'userName': '"&G2&"', 'password': 'Ssmsba1!', 'firstName': '"&E2&"', 'lastName': '"&F2&"', 'EMail': '"&D2&"',},"
adds = [
    {'userName': 'alejandro.sigaran@mytestdomain', 'password': get_random_password(), 'firstName': 'Alejandro', 'lastName': 'Sigaran', 'EMail': 'test1@gmail.com'},
    {'userName': 'tama.clark@mytestdomain', 'password': get_random_password(), 'firstName': 'Tama', 'lastName': 'Clark', 'EMail': 'test2@gmail.com'},
    {'userName': 'danielle.hershey@mytestdomain', 'password': get_random_password(), 'firstName': 'Danielle', 'lastName': 'Hershey', 'EMail': 'test3@yahoo.com'},
]

created = 0
processed = 0
target_updates = len(adds)

# Identify a template agent that has the roles/skills that you want these users to have
template_agent = client.service.getUserInfo('testguy1@aw_tam')
roles = template_agent.roles
skills = template_agent.skills

added_users = []

for user in adds:
    try:
        skills[0].userName = user['userName']
        nu = client.service.createUser({'generalInfo': user})
        # print(f'{nu.generalInfo.userName}')
        added_users.append(nu)
        created += 1
    except:
        f = user['userName']
        print(f'\nFAILED: {f}\n')
    processed += 1
    print(f'Updated:\t{created}/{target_updates}', end='\r')

print(f'Updated:\t{created}/{target_updates}')
