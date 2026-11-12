# Reference - Importing Data - Constraints

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Constraints
**Index keywords:** Constraints

---

Material schedules may be imported from a file called CONSTRAINTS.txt or CONSTRAINTS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **C.NAME** | T50 | The Constraint name. |
| C.DESCRIPTION | T15 | The Description for the Constraint |
| C.SECTION | T15 | The section to which the Constraint applies. |
| C.OPERATION | Integer | The operation external reference.. |
| C.NEWNAME | Integer | If specified, this will be used to rename the constraint (if C.NAME exists). |
| C.DELETE | Boolean | If 1 the constraint will be deleted (unless it is in use). |
