# Reference - Importing Data - Production Updates by Size Normalised

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Production Updates by Size Normalised
**Index keywords:** Productions Updates, Size Normalised

---

Production updates may be imported from a file called UPDNORM.txt or UPDNORM.csv. The operations must be flagged as being updated by size to allow size specified imports.

> **Note:** If the operation is NOT flagged to be updated by size then any sizes specified for that operation in the UPDATES file will be ignored AND the last entry in the file for an operation (any size) will be taken as the progress for that operation across all sizes, in standard size ratio.

This import file format MUST be sorted in the format of ORDER, DATE, OPERATION, SECTION, GROUP, LINE, SIZE where "date", "section", "group" and "line" are optional import fields.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **U.ORDER** | T30 | The unique order code. |
| **U.OPERATION** | Integer | The external reference of the operation. |
| **U.QTY** | Integer | Total update for the operation. |
| **U.SIZENAME** | T25 | The name of the size being updated as it appears in FastReact. |
| U.REJECTQTY | Integer | The reject quantity for this operation. |
| U.DATE | Date | The date of the update. If this field is missing then FastReact will assume that the update is for today. |
| U.LINE | T15 | The name of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. |
| U.LINE_EXTERNAL_ID | Integer | The External ID of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> 1.This field or the one above IS compulsory if Updating by Group and Row. |
| U.GROUP | T15 | The name of the planning board group on which the order is planned. If this field is missing or the group is invalid in any way then FastReact will search for the order on all planning boards. |
| U.GROUP_EXTERNAL_ID | Integer | The External ID of the group/factory for the planning board row on which the order is planned. If this field is missing or the group is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> This field or the one above IS compulsory if Updating by Group. |
| U.NOTE | T30 | This will be added as a note to the production update log for this order. |
| U.OPN_COMPLETE | T15 | This field will mark the operation as complete. <br> 0 = not complete. <br> 1 = complete. <br> This will place a check in the mark complete check box on the planned update dialog. |

Example import file:

| U.ORDER | U.OPERATION | U.SECT | U.GROUP | U.LINE | U.SIZENAME | U.QTY |
|---|---|---|---|---|---|---|
| 1550::880::BLACK | 10 | SEW | A | 1 | L | 864 |
| 1550::880::BLACK | 10 | SEW | A | 1 | M | 1152 |
| 1550::880::BLACK | 10 | SEW | A | 2 | L | 864 |
| 1550::880::BLACK | 10 | SEW | A | 2 | XL | 720 |
| 1550::880::BLACK | 30 | SEW | | | L | 100 |
| 1550::880::BLACK | 30 | SEW | | | M | 120 |
| 1550::880::BLACK | 30 | SEW | | | S | 130 |
| 1550::880::CHOCOLATE | 10 | SEW | A | 1 | 1~L | 864 |
| 1550::880::CHOCOLATE | 10 | SEW | A | 2 | 1~L | 1152 |
| 1550::880::CHOCOLATE | 10 | SEW | B | 3 | 1~L | 864 |
| 1550::880::CHOCOLATE | 10 | SEW | B | 3 | 4~XL | 720 |

## Settings = cumulative by Order.

1550::880::BLACK has progress of 2736 in operation 10 (864L+1152M+720XL)

1550::880::BLACK has progress of 350 in operation 30 (100L+120M+130S)

1550::880::CHOCOLATE has progress of 1,584 in operation 10 (864L+720XL)

## Settings = cumulative by Order, Group

1550::880::BLACK has progress of 2736 in operation 10 (864L+1152M+720XL)

1550::880::BLACK has progress of 350 in operation 30 (100L+120M+130S)

1550::880::CHOCOLATE has progress of 2,736 in operation 10 (1152L+864L+720XL)
