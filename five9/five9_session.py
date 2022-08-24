from lxml import etree
import requests
import zeep
from zeep.plugins import HistoryPlugin

from private.credentials import ACCOUNTS

# This function prints the SOAP envelope for the request and/or response
def latest_envelopes(history):
    envelopes = ""
    try:
        for hist in [history.last_sent, history.last_received]:
            e = etree.tostring(hist["envelope"], encoding="unicode", pretty_print=True)
            envelopes += e + '\n\n'
            print(e)
    except (IndexError, TypeError):
        # catch cases where it fails before being put on the wire
        pass
    
def get_client(five9username=None, five9password=None, account=None):
    # initialize the zeep history object
    history = HistoryPlugin()

    # url and user settings consolidated here for convenience to use later
    settings = {
        'FIVENINE_CONFIG_WEBSERVICES_API': 
            'https://api.five9.com/wsadmin/v12/?wsdl&user={five9username}',
    }

    if five9username == None and five9password == None:
        # Target the desired account using the alias in private.credentials
        api_account_alias = account or 'default_account'
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

    # last envelopes can be printed with
    # client.latest_envelopes(client.history)
    client.history = history
    client.latest_envelopes = latest_envelopes

    return client
