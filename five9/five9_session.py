import base64

from lxml import etree
# import os
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
        print(self.api_definition)

        # BREAKFIX - Get the directory of the current file and construct the WSDL file path
        # current_dir = os.path.dirname(os.path.realpath(__file__))
        # wsdl_file_path = os.path.join(current_dir, 'static_resources', 'config_webservices_v13.wsdl')

        try:
            super().__init__(
                self.api_definition,
                transport=zeep.Transport(session=self.transport_session),
                plugins=[self.history],
            )
            # super().__init__(
            #     wsdl_file_path,
            #     transport=zeep.Transport(session=self.transport_session),
            #     plugins=[self.history],
            # )
            self.call_counters = self.service.getCallCountersState()
            print(f"Client ready for {five9username}")

        # handle generic http errors
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, zeep.exceptions.Fault) as e:
            # pass the error to the caller through the Five9ClientCreationError exception
            raise Five9ClientCreationError(e)


    def __format_envelope(self, envelope):
        """
        Formats the SOAP envelope for printing.

        Args:
            envelope: The SOAP envelope to format.

        Returns:
            A formatted string containing the SOAP envelope.
        """
        return etree.tostring(envelope, encoding="unicode", pretty_print=True)


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

    @property
    def latest_envelope_sent(self):
        """
        Returns the latest SOAP envelope that was sent by the client as a string.

        Returns:
            A string containing the latest SOAP envelope that was sent by the client.
            If no envelope is available, an empty string is returned.
        """
        try:
            return self.__format_envelope(self.history.last_sent["envelope"])
        except (AttributeError, IndexError, TypeError):
            # catch cases where the history object was altered to an invalid type
            # re-initialize the history object
            self.history = HistoryPlugin()

            return ""

    @property    
    def latest_envelope_received(self):
        """
        Returns the latest SOAP envelope that was received by the client as a string.

        Returns:
            A string containing the latest SOAP envelope that was received by the client.
            If no envelope is available, an empty string is returned.
        """
        try:
            return self.__format_envelope(self.history.last_received["envelope"])
        except (AttributeError, IndexError, TypeError):
            # catch cases where the history object was altered to an invalid type
            # re-initialize the history object
            self.history = HistoryPlugin()

            return ""

    @property
    def latest_request_headers(self):
        """
        Prints the latest request with headers and body.
        """
        last_request = self.history.last_sent
        request_string = ""
        if last_request:
            headers = last_request["http_headers"]

            for key, value in headers.items():
                request_string += f"{key}: {value}\n"

            # Print Basic Auth header
            auth = f"{self.transport_session.auth.username}:{self.transport_session.auth.password}"
            # base64 encode the username and password from the session
            auth_header_value = base64.b64encode(auth.encode("utf-8")).decode("utf-8")

            if auth_header_value:
                request_string += f"Authorization: {auth_header_value}"
            
            return request_string

        else:
            return "No request found in history"

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
    