# Reference - Importing Data - Plan Constraints

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Plan Constraints
**Index keywords:** Plan Constraints

---

Attended Time details may be imported from a file called PLAN_CONSTRAINTS.txt or PLAN_CONSTRAINTS.csv

The following fields may be imported. Essential fields are shown in bold, other fields may be omitted.

| Field Name | Type | Description |
|---|---|---|
| **C.GROUP_NAME** | T15 | The name of the Group. |
| **C.GROUP_EXTERNAL_ID** | T15 | The external ID of the Group. |
| **C.CONSTRAINT_NAME** | T15 | The Constraint name. |
| C.ROW_NAME | T15 | The Row name. |
| C.ROW_EXTERNAL_ID | Integer | The external ID of the Row. |
| C.CAPACITY | FLOAT | The capacity of the Group with the Constraint. |

> **Note:** Row can be optional, Name or external id can be used but both are not needed. Capacity of zero or not present deletes constraint.
