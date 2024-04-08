# getStatistics Flow

1. setSessionParameters
    - this step initializes the session with the type of statistics being requested.  Optionally you can specify what columns you want to include from that data set if you don't need them all

2. getStatistics
    - Initial request of the statistics.  Returns a timestamp value to show the time through which the data is current

3. getStatisticsUpdate (optional)
    - optionally, call this method in a long-running loop, using the timestamp from the initial getStatistics method as the starting point.  This method also includes a timestamp parameter to use subsequently to obtain only the statistics that changed since the last update.

## Important

The Five9 API operates on a single-threaded model, meaning that it can process only one request at a time. Consequently, all requests to fetch statistics or receive updates must be made in a sequential order. This approach ensures that each request is completed before the next one begins, maintaining the integrity of the session's workflow.


For sessions that may track multiple types of statistics (e.g., AgentState, AgentStatistics, ACDStatus), design such that each statistics category maintains its own "previous timestamp" value for use in the statistics update request for that statistics type.

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

# setSession Notes

Each Statistics API client session must be initialized with viewSettings options

    view_settings = {
        "forceLogoutSession": "yes",
        # [Minutes5,Minutes10,Minutes15,Minutes30,Hour1,Hours2,Hours3,Today]
        "rollingPeriod": "Today",
        "shiftStart": "28800000",
        "statisticsRange": "CurrentWeek",
        "timeZone": "-25200000",
    }

note that the shiftStart is the starting time for the day’s shift in milliseconds starting at midnight. Used to calculate certain statistics.

  - Example: 8 AM = 8h x 60m x 60s x 1000 ms = 28,800,000 ms

The timeZone option is also an offset in milliseconds since midnight.  
  
  - Example: PST(-7h GMT) = 7h x 60m x 60s x 1000 ms = 25,200,000 ms

rollingPeriod is the time range used to calculate aggregate statistics in Outbound Campaign Manager; corresponds to Campaign Manager Rolling Period in the Supervisor VCC.

statisticsRange is the time interval for aggregate statistics.  Options are:

  - [RollingHour, CurrentDay, CurrentWeek, CurrentMonth, Lifetime, CurrentShift]