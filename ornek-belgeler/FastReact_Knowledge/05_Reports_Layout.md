# Main Menu - Reports - Layout

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports > Layout
**Index keywords:** Layout

---

## Formula Options within Reporting Fields.

| Function | Description | Example |
|---|---|---|
| @SUM | Sum of repeating values between report date range. | @SUM([O.QTY_WEEK~1]) |
| @EARLIER | Sum of repeating values earlier than specified date range. | @EARLIER([O.QTY_WEEK~1]) |
| @LATER | Sum of repeating values later than specified date range. | @LATER([O.QTY_WEEK~1]) |
| @SUMALL | Sum of all repeating fields above. | @SUMALL([O.QTY_WEEK~1]) |
| @AVE | Straight average of repeating values between report date range. | @AVE([O.QTY_WEEK~1]) |
| @AVENZ | Average excluding zero’s of repeating values between report date range. | @AVENZ([O.QTY_WEEK~1]) |
| @COUNT | Number of periods in date range. | @COUNT([O.QTY_WEEK~1]) |
| @COUNTNZ | Number of periods having a value in a date range. | @COUNTNZ([O.QTY_WEEK~1]) |
| @MAX | Greatest value in a date range. | @MAX([O.QTY_WEEK~1]) |
| @MIN | Lowest value in a date range. | @MIN([O.QTY_WEEK~1]) |
| @MINNZ | Lowest non zero value in a date range. | @MINNZ([O.QTY_WEEK~1]) |
| @ROUND | Rounds any value up or down. | 10.5 would become 1110.4 would become 10 |
| @ROUNDUP | Always rounds a value up. | 10.5 would become 1110.4 would become 11 |
| @ROUNDDOWN | Always rounds a value down. | 10.5 would become 1010.4 would become 10 |
| @SELECT | The standard "If" statement in FastReact. | @SELECT([O.DAYS_LATE]:<0:URGENT,OK) <br> The example above will enter ' Urgent ' in the report field if the order days late for delivery is < 1 if >1 then it enters ' OK' . |
| @SELECTNUM | The standard "If" statement in FastReact when the output is for a number . | @SELECTNUM([O.DAYS_LATE]:<0:1,0) <br> The example above will enter 1 in the report field if the order days late for delivery is < 1 if >1 then it enters 0. |
| @SELECTDATE | The standard "If" statement in FastReact when the output is for a date . | @SELECTDATE([O.EVENTS_DONE~8]:>0:[O.EVENTS_DONE~8],[O.EVENTS_TARGET~8]) <br> Will report the completed date of an event if there is one, otherwise the target date will be reported. |
| @DTVAR | Difference between 2 dates. | @DTVAR([TODAY]-[O.AVAIL_CUST_END]) |
| @WEEKSTART | This will give the first date of the week that the selected date is in. | |
| @WEEKEND | This will give the last date of the week that the selected date is in. | |
| @MONTHSTART | This will give the first date of the month that the selected date is in. | |
| @MONTHEND | This will give the last date of the month that the selected date is in. | |
| @CONCAT | This Function will take a series of values in the form of hard coded text, actual reporting fields or cell references , and concatenate them together within a single cell. | @CONCAT([O.CUST],"::", {{A2}} ,"::",[O.DEL_DATES~1]) <br> @ CONCAT([O.CUST],::,{{A2}},<COMMA>,[O.DEL_DATES~1]) <br> If a comma is required in the concatenation the n a special text value ‘<COMMA>’ (without the quotes) is required . |
| @CONCATRPT | As above, but used with repeating fields. | @CONCATRPT([O.QTY_WEEK~1],[O.CODE],[O.QTY_WEEK~1]) <br> This will allow repeating for weeks, but the result will concatenate only the Order Code and Weekly quantity. |
| < | Reports the lower of 2 values in a calculation. | 100<@SUM([O.QTY_WEEK~1]) |

*(table continued)*

| Function | Description | Example |
|---|---|---|
| > | Reports the Higher of 2 values in a calculation. | 100>@SUM([O.QTY_WEEK~1]) |
