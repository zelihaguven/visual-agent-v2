# Reference - Importing Data - Production Updates

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Production Updates
**Index keywords:** Productions Updates

---

Production updates may be imported from a file called UPDATE.txt or UPDATE.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **U.ORDER** | T30 | The unique order code. |
| **U.DATE** | Date | The date of the update. If this field is missing then FastReact will assume that the update is for today. |
| **U.QTY** | Integer | The quantity of production to be updated from the planning board. <br> Note: <br> This field represents the Planned Operation and as such the O^PQ field for the Planned operation should not be included. |
| U.SECT | T15 | The name of the planning board section in which the order is planned. <br> Note: <br> This field IS compulsory in a multi section environment. |
| U.GROUP | T15 | The name of the group/factory for the planning board row on which the order is planned. If this field is missing or the group is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> This field or the one below IS compulsory if Updating by Group. |
| U.GROUP_EXTERNAL_ID | Integer | The External ID of the group/factory for the planning board row on which the order is planned. If this field is missing or the group is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> This field or the one above IS compulsory if Updating by Group. |
| U.LINE | T15 | The name of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> 1. If sequence characters are used in the defining of the Row then they must also be present in the U.LINE field. For Example, the Row is defined as " 10 Line 1 ", in the import it states " Line 1 " then this will be classed as an invalid Row. The correct field in the Import file will say " 10 Line 1 ". <br> 2. This field or the one below IS compulsory if Updating by Group and Row. |
| U.LINE_EXTERNAL_ID | Integer | The External ID of the planning board row on which the order is planned. If this field is missing or the row is invalid in any way then FastReact will search for the order on all planning boards. <br> Note: <br> 1.This field or the one above IS compulsory if Updating by Group and Row. |
| U.COMPLETE | Integer | Indicates whether the Planned Operation is complete in the specified section, regardless of the quantity that has been completed against that operation. <br> 0 = not complete. <br> 1 = complete. |
| U^PQ: n | Float | The production update to be applied to individual operations where ' n ' = External reference for the operation. |
| U^RQ: n | Float | The reject quantity for the specified operation where ' n ' = External reference for the operation. |
| U.NOTE | T30 | This will be added as a note to the production update log for this order. <br> Note: <br> The Note can ONLY be applied to the Planned operation in this Update format. In order for the Planned Operation Note to be4 applied the Planned Operation must have some production in the import file. |
| U^OMC: n | | This field will mark the operation as complete, where ' n ' = External reference for the operation. <br> Note: <br> 1. U^OMC: MUST be in same sequence as U^PQ: and MUST be the same count. <br> 2. Due to the fact that the Planned Update does not use the U^PQ method FastReact cannot use U^OMC to complete the Planned operation. |

The U.Group_External_ID and the U.Group should be used independently of each other, the same is true for U.Line_External_ID and the U.Line.
