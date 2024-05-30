from five9 import five9_session

client = five9_session.Five9Client()

# set the target list name
target_list = "outreach"


list_update_settings = {
    "fieldsMapping": [
        # fieldsMapping objects to map data to the columns
        # Note that the key fields combine to create unique-together constraints that are used
        # to create or update the underlying contact records.
        {"columnNumber": 1, "fieldName": "number1", "key": "false"},
        {"columnNumber": 2, "fieldName": "uuid", "key": "true"},
        {"columnNumber": 3, "fieldName": "email", "key": "false"},
    ],
    "callNowMode": "true",  # set to true to add to the ASAP queue
    # "callTime": "1651260618000", # epoch milliseconds, applies if callNowMode is true
    "allowDataCleanup": "true",
    "skipHeaderLine": "false",
    "cleanListBeforeUpdate": "false",  # set True to wipe the list clean before import
    "crmAddMode": "ADD_NEW",
    "crmUpdateMode": "UPDATE_FIRST",  # CAUTION - ensure proper record key values are set
    "listAddMode": "ADD_FIRST",  # if multiple contactDB records are matched, determine if multiple list entries should be added.
}


records_to_add = {
    "values": [
        ["9133259337", "abcd123456789", "anrew@livingston.com"],
    ]
}

# add a single record to the designated list
result_identifier = client.service.addRecordToList(
    listName=target_list,
    listUpdateSettings=list_update_settings,
    importData=records_to_add,
)

# uncomment to see the latest envelopes
print(client.latest_envelopes)
