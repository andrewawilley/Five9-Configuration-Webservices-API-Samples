# getStatistics Flow

1. setSessionParameters
    - this step initializes the session with the type of statistics being requested.  Optionally you can specify what columns you want to include from that data set if you don't need them all

2. getStatistics
    - Initial request of the statistics.  Returns a timestamp value to show the time through which the data is current

3. getStatisticsUpdate (optional)
    - optionally, call thsi method in a long-running loop, using the timestamp from the initial getStatistics method as the starting point.  This method also includes a timestamp parameter to use subsequently to obtain only the statistics that changed since the last update.

# statisticType

Per Page 31 of the Statistics Webservices API documentation, the following statisticTypes are available on the endpoint:

| statisticType | Description|
|---------------|------------|
|AgentState|Status of each agent.|
|AgentStatistics|Statistics for each agent.|
|ACDStatus|Information about skill group queues.|
|CampaignState|Current status of all campaigns.|
|OutboundCampaignManager|Information about outbound campaigns that are running.|
|OutboundCampaignStatistics|Statistics about outbound campaigns.|
|InboundCampaignStatistics|Statistics about inbound campaigns.|
|AutodialCampaignStatistics|Statistics about autodial campaigns.|

