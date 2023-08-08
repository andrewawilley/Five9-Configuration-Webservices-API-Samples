Running reports and retrieving the result still relies on defined report definitions and structure in the Five9 Standard Reports interface

Ensure that you the report structure that you want defined there.  In the API request, you will perform three steps:

  1. **runReport** - this requests invokes a report to be run, and you will specify the report folder and report name, as well as the desired timeframe of the report (just like you would if you were running the report on the web.  This API method returns a "reportRunId".
  2. **isReportRunning** - perform checks to see if the report has completed.  You will pass in the reportId from the runReport request.  **DO NOT run this request in a loop**, it DOES consume API limits.  Make timed requests on some interval (5 seconds for example) to avoid using up all your API useage quota
  3. **getReporResult** and **getReportResultCsv** - these methods will return the contents of the report.  I recommend using the getReportResultCsv as it has a higher row capacity. 

See the runReport.py sample script for an example of how to run a report and retrieve the results.
