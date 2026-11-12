# Reference - Importing Data - Operation Descriptors

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Operation Descriptors
**Index keywords:** Importing Data, Operation Descriptors

---

Product Operations may be imported from a file called OPNDESCS.txt or OPNDESCS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **D.NAME** | T30 | The Descriptor Code/Name. |
| D.DESCRIPTION | Date | The Descriptor Description. |
| D.NEWNAME | Integer | The new Descriptor Code/Name. If specified, it will be used to rename the descriptor (if D.NAME exists). |
| D.DELETE | Integer | if D.DELETE = 1 then the descriptor will be deleted, unless it is in use. |
