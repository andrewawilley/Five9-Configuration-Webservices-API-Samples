from lxml import etree
import requests
import zeep
from zeep.plugins import HistoryPlugin

from private.credentials import ACCOUNTS

# This function prints the SOAP envelope for the request and/or response
def latest_envelope(history, last_sent=True, last_received=True):
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

def get_client(five9username=None, five9password=None):
    # initialize the zeep history object
    history = HistoryPlugin()

    # url and user settings consolidated here for convenience to use later
    settings = {
        'FIVENINE_CONFIG_WEBSERVICES_API': 
            'https://api.five9.com/wsadmin/v12/?wsdl&user={five9username}',
    }

    if five9username == None:
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
        print(f'Authenticated as {five9username}')
    except requests.exceptions.HTTPError as e:
        client = None
        print(e)

    client.history = history
    client.latest_envelope = latest_envelope

    return client
