from setuptools import setup, find_packages
import os


# create files that will be excluded from the repository from list of tuples
# first tuple element is the filename with directory, second is the file content
files_to_create = [
    ("private/credentials.py", 
        '''
# update the below with the desired credential for semi-secure re-use credentials
# When kept in the private folder, it will not be incldued in git commits
# This is NOT a good/secure practice.  Consider implementing a database store
# or using command line arguments.  This is simply for demonstration purposes.

ACCOUNTS = {
    'default_account': {
        'username': 'apiUserUsername',
        'password': 'apiUserPassword'
    },
}
'''),
    ("private/__init__.py", ""),
    ("private/users_to_update.csv", "")
]

for new_file in files_to_create:
    # create the directories for the files that will be generated
    os.makedirs(os.path.dirname(new_file[0]), exist_ok=True)
    # write the file contents
    with open(new_file[0], "w") as f: f.write(new_file[1])

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='five9',
    version='1.1.0',
    packages=find_packages(),
    description='A Five9 Configuration Webserivce API wrapper',
    long_description=open('README.md').read(),
    install_requires=requirements,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
    ],
)

