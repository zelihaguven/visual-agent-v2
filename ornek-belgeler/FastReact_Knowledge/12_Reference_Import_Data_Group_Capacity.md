# Reference - Importing Data - Group Capacity

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Group Capacity
**Index keywords:** Group Capacity

---

Group Capacity details may be imported from a file called GROUPCAPACITY.txt or GROUPCAPACITY.csv

The following fields may be imported. Essential fields are shown in bold, other fields may be omitted.

| Field Name | Type | Description |
|---|---|---|
| **GC.GROUP_ID** | Integer | External ID for the Group. |
| **GC.OP_ID** | Integer | External ID for the Operation. |
| **GC.DATE** | Date | The date that the Capacity is due to change. |
| **GC.CAPACITY** | Integer | The new Capacity per hour (x1000) |
| GC.NOTE | T128 | The Note against this change. |

> **Note:** The routine will only import operations where 'Ignore operation in loading barcharts' = FALSE (not ticked)

Multiple updates for the same operation and group will need to be grouped/ordered together.

The routine will delete any existing capacity changes
