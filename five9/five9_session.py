from lxml import etree
import requests
import zeep
from zeep.plugins import HistoryPlugin

from private.credentials import ACCOUNTS


class Five9ClientCreationError(Exception):
    pass


class Five9Client(zeep.Client):
    call_counters = None
    history = None

    def __init__(self, *args, **kwargs):
        five9username = kwargs.get("five9username", None)
        five9password = kwargs.get("five9password", None)
        account = kwargs.get("account", None)
        api_hostname = kwargs.get("api_hostname", "api.five9.com")
        api_version = kwargs.get("api_version", "v12")

        self.history = HistoryPlugin()

        # url and user settings consolidated here for convenience to use later
        api_definition_base = "https://{api_hostname}/wsadmin/{api_version}/?wsdl&user={five9username}"
        

        if five9username == None and five9password == None:
            # Target the desired account using the alias in private.credentials
            api_account_alias = account or "default_account"
            api_account = ACCOUNTS.get(api_account_alias, {})

            five9username = api_account.get("username", None)
            five9password = api_account.get("password", None)

        # prepare the session with BasicAuth headers
        self.transport_session = requests.Session()
        self.transport_session.auth = requests.auth.HTTPBasicAuth(five9username, five9password)

        self.api_definition = api_definition_base.format(
            api_hostname=api_hostname, api_version=api_version, five9username=five9username
        )
        # print(api_definition)

        try:
            super().__init__(
                self.api_definition,
                transport=zeep.Transport(session=self.transport_session),
                plugins=[self.history],
            )
            self.call_counters = self.service.getCallCountersState()
            print(f"Client ready for {five9username}")

        # handle generic http errors
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, zeep.exceptions.Fault) as e:
            # pass the error to the caller through the Five9ClientCreationError exception
            raise Five9ClientCreationError(e)


    @property
    def latest_envelopes(self):
        """
        Returns the latest SOAP envelopes that were sent or received by the client as a string.

        Returns:
            A string containing the latest SOAP envelopes that were sent or received by the client.
            If no envelopes are available, an empty string is returned.
        """
        envelopes = ""
        try:
            for hist in [self.history.last_sent, self.history.last_received]:
                e = etree.tostring(
                    hist["envelope"], encoding="unicode", pretty_print=True
                )
                envelopes += e + "\n\n"
            return envelopes
        except (AttributeError, IndexError, TypeError):
            # catch cases where the history object was altered to an invalid type
            # re-initialize the history object
            envelopes = "History object not found.  Re-initializing the history object.\n\n"
            self.history = HistoryPlugin()

            return envelopes

    # TODO class method to obtain the domain rate limits to update a class property
    # that helps bake in a delay between requests if needed


    def print_available_service_methods(self, print_methods=True):
        """
        Prints the available methods for the client.
        """
        print("Available methods:")
        # create sorted list of methods from the service
        methods = sorted(self.service._operations.keys())
        for method in methods:
            print(f"\t{method}")
    