# Reference - Importing Data - Production Updates By Size

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Production Updates By Size
**Index keywords:** Production Updates By Size

---

Production updates may be imported from a file called UPDATE.txt or UPDATE.csv.

The following fields may be imported. Essential fields are shown in bold.

> **NOTE:**

- This import file format require the Import option, "Import normalised production updates" to be enabled.
- Although the file format is called Production Updates by Size, sizes are not a required field.

| Field Name | Type | Description |
|---|---|---|
| **U.ORDER** | T30 | The unique order code. |
| **U.OPERATION** | Integer | The external reference of the operation. |
| **U.QTY** | Integer | Total update for the operation. |
| U^SIZENAME: n | T25 | The name of the size being updated, where ' n ' = a sequential number. |
| U^SIZEQTY: n | Integer | The quantity of the production update for the size, where ' n ' = the same sequential number as the appropriate U^SIZENAME. |
| U.REJECTQTY | Integer | The reject quantity for this operation. |
| The following items are for planned operations only | | |
| U.DATE | Date | The date of the update. If this field is missing then FastReact will assume that the update is for today. |
| U.LINE | T15 | The name of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. |
| U.LINE_EXTERNAL_ID | Integer | The External ID of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> 1.This field or the one above IS compulsory if Updating by Group and Row. |
| U.GROUP | T15 | The name of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. |
| U.GROUP_EXTERNAL_ID | Integer | The External ID of the group/factory for the planning board row on which the order is planned. If this field is missing or the group is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> This field or the one above IS compulsory if Updating by Group. |
| U.SECT | T15 | The name of the planning board section in which the order is planned. <br> Note: <br> This field IS compulsory in a multi section environment. |
| U.COMPLETE | Integer | Indicates whether the Planned Operation is complete in the specified section, regardless of the quantity that has been completed against that operation: <br> 0 = not complete <br> 1 = complete <br> This will place a check in the mark complete check box on the Update dialog for the planned operation. <br> Note: <br> To avoid confusion it is recommended to use the U.OPN_COMPLETE field header rather than U.COMPLETE. |
| U.NOTE | T30 | This will be added as a note to the production update log for the defined operation. |
| U.OPN_COMPLETE | T15 | This field will mark the Operation as complete. <br> 0 = not complete. <br> 1 = complete. <br> This will place a check in the mark complete check box on the Update dialog. |

Example import file

| U.ORDER | U.OPERATION | U.QTY | U.REJECTQTY | U^SIZENAME:1 | U^SIZENAME:2 | U^SIZEQTY:1 | U^SIZEQTY:2 | U.DATE | U.SECT | U.GROUP | U.LINE | U.OPN_COMPLETE | U.NOTE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ORDER1 | 10 | 1000 | 100 | | | | | 18/09/2008 | SEW | Factory 1 | | 1 | |
| ORDER1 | 20 | 800 | 40 | 001 S | 002 M | 200 | 200 | 18/09/2008 | SEW | Factory 1 | | 0 | |
| ORDER1 | 30 | 500 | 10 | | | | | 18/09/2008 | SEW | Factory 1 | | 0 | |
| ORDER1 | 35 | 480 | 11 | | | | | 18/09/2008 | SEW | Factory 1 | | 0 | |
| ORDER1 | 40 | 400 | 5 | 001 S | 002 M | 100 | 100 | 18/09/2008 | SEW | Factory 1 | Line _ 01 | 0 | Low due to ABS. |
| ORDER1 | 50 | 300 | 0 | | | | | 18/09/2008 | SEW | Factory 1 | | 0 | |
| ORDER1 | 60 | 200 | 2 | | | | | 18/09/2008 | SEW | Factory 1 | | 0 | |
