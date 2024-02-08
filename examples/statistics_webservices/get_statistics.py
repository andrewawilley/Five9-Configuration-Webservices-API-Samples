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
    print("No saved account credentials discovered")
    ACCOUNTS = {}

################################################################################
# This section could be moved into a re-usable module, but for the sake of
# example is verbose and not optomized.


# This function prints the SOAP envelope for the request and/or response
def zeep_history_print(history, last_sent=True, last_received=True):
    try:
        if last_sent is True:
            print(
                etree.tostring(
                    history.last_sent["envelope"], encoding="unicode", pretty_print=True
                )
            )
        if last_received is True:
            print(
                etree.tostring(
                    history.last_received["envelope"],
                    encoding="unicode",
                    pretty_print=True,
                )
            )
    except (IndexError, TypeError):
        # noncritical if fails here, pass
        pass


# initialize the zeep history object
history = HistoryPlugin()

# url and user settings consolidated here for convenience to use later
settings = {
    "FIVENINE_CONFIG_WEBSERVICES_API": "https://api.five9.com/wssupervisor/v12/SupervisorWebService?wsdl&user={five9username}",
}


# Target the desired account using the alias in private.credentials
api_account_alias = "default_account"
api_account = ACCOUNTS.get(api_account_alias, {})

if api_account.get("username", None) in [None, "apiUserUsername"]:
    five9username = input("Enter Username: ")
    five9password = input("Enter Password: ")
else:
    five9username = api_account.get("username", None)
    five9password = api_account.get("password", None)

# prepare the session with BasicAuth headers
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(five9username, five9password)
try:
    client = zeep.Client(
        settings["FIVENINE_CONFIG_WEBSERVICES_API"].format(five9username=five9username),
        transport=zeep.Transport(session=session),
        plugins=[
            history,
        ],
    )
    print(f"Client created successfully for {five9username}")
except requests.exceptions.HTTPError as e:
    client = None
    print(e)
################################################################################


# this method needs to be called to initialize the session


def set_session_parameters(view_settings=None):
    # page 59 of the Statistics Webservices API Reference Guide
    if view_settings is None:
        view_settings = {
            "forceLogoutSession": "yes",
            # [Minutes5,Minutes10,Minutes15,Minutes30,Hour1,Hours2,Hours3,Today]
            "rollingPeriod": "Today",
            "shiftStart": "28800000",
            "statisticsRange": "CurrentWeek",
            "timeZone": "-25200000",
        }
    client.service.setSessionParameters(viewSettings=view_settings)
    # c = client.service.getColumnNames('AgentState')
    # print(c)


def get_specific_statistics(statistics_request_type, statistics_request_columns):
    set_session_parameters()
    c = client.service.getColumnNames()
    print(c)
    return client.service.getStatistics(
        statisticType=statistics_request_type, columnNames=statistics_request_columns
    )


def get_statistics(statistics_request_type):
    set_session_parameters()
    return client.service.getStatistics(statisticType=statistics_request_type)


statistics_request_type = "AgentStatistics"
# statistics_request_type = "AgentState"
# Optionally specify only the columns desired for the statistics updates
statistics_request_columns = {
    "values": {"data": ["Username", "Full Name", "State", "State Since"]}
}

set_session_parameters()

# If you only need certain columns returned:
specific_statistics = get_specific_statistics(
    statistics_request_type, statistics_request_columns
)

print(specific_statistics)
# statistics = get_statistics(statistics_request_type)

# statistics_timestamp = statistics.timestamp

# statistics_update = client.service.getStatisticsUpdate(
#     statisticType=statistics_request_type,
#     previousTimestamp=statistics_timestamp,
#     longPollingTimeout=5000,
# )

# if putting statistics_update in a loop, use statistics_update.lastTimestamp
# in subsequent update requests.
