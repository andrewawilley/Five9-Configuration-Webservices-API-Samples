import csv
import datetime
import time

from lxml import etree
import requests
import zeep
from zeep.plugins import HistoryPlugin

try:
    import sys
    sys.path.append("..") 
    from private.credentials import ACCOUNTS
except:
    print('No saved account credentials discovered')
    ACCOUNTS = {}

# This function prints the SOAP envelope for the request and/or response
def zeep_history_print(history, last_sent=True, last_received=True):
    try:
        if last_sent is True:
            print(etree.tostring(
                history.last_sent["envelope"], 
                encoding="unicode", 
                pretty_print=True))
        if last_received is True:
            print(etree.tostring(
                history.last_received["envelope"],
                encoding="unicode",
                pretty_print=True))
    except (IndexError, TypeError):
        # noncritical if fails here, pass
        pass

# initialize the zeep history object
history = HistoryPlugin()

# url and user settings consolidated here for convenience to use later
settings = {
    'FIVENINE_CONFIG_WEBSERVICES_API': 
        'https://api.five9.com/wsadmin/v12/?wsdl&user={five9username}',
 }


# Target the desired account using the alias in private.credentials
api_account_alias = 'default_account'
api_account = ACCOUNTS.get(api_account_alias, {})

if api_account.get('username', None) in [None, 'apiUserUsername']:
    five9username = input('Enter Username: ')
    five9password = input('Enter Password: ')
else:
    five9username = api_account.get('username', None)
    five9password = api_account.get('password', None)

# prepare the session with BasicAuth headers
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(five9username, five9password)
try:
    client = zeep.Client(
        settings['FIVENINE_CONFIG_WEBSERVICES_API'].format(
            five9username=five9username),
        transport=zeep.Transport(session=session),
        plugins=[history,]
    )
except requests.exceptions.HTTPError as e:
    client = None
    print(e)


listUpdateSettings={
    "fieldsMapping": [
        # fieldsMapping objects to map data to the columns
        {"columnNumber": 1, "fieldName": "number1", "key": "false"},
        {"columnNumber": 2, "fieldName": "email", "key": "true"},
        {"columnNumber": 3, "fieldName": "first_name", "key": "false"},
    ],
    "allowDataCleanup": "true",
    "skipHeaderLine": "false",
    "cleanListBeforeUpdate": "false", # set True to wipe the list clean before import
    "crmAddMode": "ADD_NEW",
    "crmUpdateMode": "DONT_UPDATE", # CAUTION - ensure proper record key values are set
    "listAddMode": "ADD_FIRST", # if multiple contactDB records matched, determine if multiple list entries should be added.
    #"callTime": 1632950195000,
    #"callTimeColumnNumber": 4
}

importData=[
    {
        "values": [
                "9138675309",
                "anrew@livingston.com",
                "Anrew",
            ]
    },
    {
        "values": [
                "8168675309",
                "alex@livingston.com",
                "Alex",
            ]
    },
],    

result_identifier = client.service.asyncAddRecordsToList(listName="outreach",
    listUpdateSettings=listUpdateSettings, importData=importData)

print(history.last_sent)

import_result = client.service.getListImportResult(identifier=result_identifier)
