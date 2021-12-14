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

# Change to your target dates and target folder / report name.  
# These folder and report names come from 
# the "Custom Reports" section in Five9 reporting portal
criteria_datetime_start = datetime.date.today()
criteria_datetime_end = datetime.date.today() + datetime.timedelta(days=1)
report_folder = "staging"
report_name = "staging_callLog"

# Criteria object contains required parameters forthe runReport method
report_criteria = {
    "time": {
        "start": criteria_datetime_start.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "end": criteria_datetime_end.strftime("%Y-%m-%dT%H:%M:%S.000"),
    },
    # Optionally filter the report by an additional objectType <work in progress>
    # This is generally best done in the report definition in the Five9 portal. 
    # In the below example, the report could be filtered for records where
    # the skill is equal to sample skills "omni" or "outreach_en"
    # 
    # "reportObjects": {
    #     "objectNames": [
    #         "omni", 
    #         "outreach_en",
    #     ],
    #     "objectType": "Skill",
    # }

    # reportObjects can by of objectType
    #       AgentGroup
    #       Campaign
    #       CampaignProfile
    #       CrmField
    #       Disposition
    #       List
    #       Prompt
    #       ReasonCode
    #       Skill
    #       User
    #       UserProfile
    #       IvrScript
    #       CallVariableGroup
    #       CallVariable
    #       Connector
}



# Request the report to be generated.  Will respond with a report run ID
try:
    report_run_id = client.service.runReport(
        folderName=report_folder,
        reportName=report_name,
        criteria=report_criteria)
    print(f'Report Id Requested: {report_run_id}')
except zeep.exceptions.Fault as e:
    print(e)




# Sample soap envelope payloads for the runReport request and response
print('\nSOAP envelopes for request and response:')
zeep_history_print(history)

# Check to see if the report has finished running.
# IMPORTANT: failure to pause for some time between each check to see if the 
# report has run can cause you to exceed your API limits.
report_running = True
checks = 0
while report_running is True:
    report_running = client.service.isReportRunning(report_run_id, timeout=10)
    if report_running is True:
        print(f"Still Running ({checks})", end="\r")
        # IMPORTANT - invoking this method on a loop for a long-running report 
        # WILL burn up your API rate limits, put some time between requests
        time.sleep(5)

print("DONE Running")

# Csv result set is faster to obtain, less verbose response body
reportResultCsv = client.service.getReportResultCsv(report_run_id)
row_count_in_result_csv = len(reportResultCsv)-1
print(reportResultCsv)

# This is more convenient if you don't want to parse the csv data
reportResult = client.service.getReportResult(report_run_id)

row_count_in_result = len(reportResult.records)
print(f'Row count: {row_count_in_result}\n')

# print(reportResult)

# Insert the data into your database 
# or write to a file for another process to consume
