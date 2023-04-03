# Quickstart

The purpose of this repository is to provide individually functional scripts to demonstrate how to use Five9 Configuration Webservices API methods in Python.

### Obtain the repository

It is highly recommended that you install [git](https://git-scm.com/download/win) so that you can update to the latest version of this repository as needed.  Once installed, from the command line you can clone this repository with

    git clone https://github.com/andrewawilley/Five9-Configuration-Webservices-API-Samples.git

You can also just download a [zip archive](https://github.com/andrewawilley/Five9-Configuration-Webservices-API-Samples/archive/refs/heads/main.zip) of the repository and extract

from the shell, navigate to the local copy (change to the directory that the repository is located) and then ...

#### Windows Users
    mkdir venvs
    cd venvs
    py.exe -m venv five9
    cd ..
    .\venvs\five9\Scripts\activate

#### Mac/Linux Users
    mkdir venvs
    cd venvs
    python3 -m venv five9
    cd ..
    source venvs/five9/bin/activate

### finishing up
    pip install -r requirements.txt
    py.exe bootstrap.py

The bootstrap.py script will create a private folder that can contain a credentials.py file where you can keep reusable Five9 admin API user credentials in a slightly more secure way than right in the script.  The private folder is excluded from Git.  

The credentials object in private.credentials looks like this:

    ACCOUNTS = {
        'default_account': {
            'username': 'apiUserName',
            'password': 'superSecretPassword'
        }
    }

If you run a script without this accounts object, you'll be prompted to enter username and password in the console. 

# Creating and using a shell session
After activating the virtual evnironment and starting a python shell, an authenticated client can be obtained using the included five9_session.py

import five9_session
client = five9_session.Five9Client()

This creates an authenticated client object that can invoke any of the API endpoints.  For example:

    call_variables = client.service.getCallVariables()

The most recent SOAP envelope content can be viewed with 

    print(client.latest_envelopes)

To print all the 
