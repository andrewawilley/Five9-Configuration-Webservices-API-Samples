# Quickstart

The purpose of this repository is to provide individually functional scripts to demonstrate how to use Five9 Configuration Webservices API methods

### Windows Users
    mkdir venvs
    cd venvs
    py.exe -m venv five9
    cd ..
    .\venvs\five9\Scripts\activate

### Mac/Linux Users
    mkdir venvs
    cd venvs
    python3 -m venv five9
    cd ..
    source venvs/five9/bin/activate

### finishing up
    pip install -r requirements.txt
    py.exe bootstrap.py

The bootstrap.py script will create a private folder that can contain a credentials.py file where you can keep reusable Five9 admin API user credentials in a slightly more secure way than right in the script.  The private folder is excluded from Git.  

The credentials object looks like this:

    ACCOUNTS = {
        'default_account': {
            'username': 'apiUserName',
            'password': 'superSecretPassword'
        }
    }

If you run a script without this accounts object, you'll be prompted to enter username and password in the console. 

# Creating and using a shell session
After activating the virtual evnironment and starting a python shell

    from five9_session import *
    client = five9_session.get_client()

This will return a client object that can invoke any of the API endpoints.  For example:

    call_variables = client.service.getCallVariables()
