from five9 import five9_session

client = five9_session.Five9Client()

# set the target list name
target_list = "outreach"


list_delete_settings = {
    "fieldsMapping": [
        # fieldsMapping objects to map data to the columns
        # Note that the key fields combine to create unique-together constraints that are used
        # to create or update the underlying contact records.
        {"columnNumber": 1, "fieldName": "number1", "key": "true"},
        {"columnNumber": 2, "fieldName": "uuid", "key": "true"},
    ],
    # "callTime": "1651260618000", # epoch milliseconds, applies if callNowMode is true
    "skipHeaderLine": "false",
    "listDeleteMode": "DELETE_ALL",  # if multiple contactDB records are matched, determine if multiple list entries should be added.
}


record_to_remove = {"fields": ["9135554444","abcd1234567"]}


# add a single record to the designated list
result_identifier = client.service.deleteRecordFromList(
    listName=target_list,
    listDeleteSettings=list_delete_settings,
    record=record_to_remove,
)

# uncomment to see the latest envelopes
print(client.latest_envelopes)
