# Reference - Importing Data - Flows

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Flows
**Index keywords:** Flows

---

Production flows may be imported from a file called FLOWS.txt or FLOWS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **F.NAME** | T30 | The flow name. |
| **F.DATE** | T50 | The week ending date for the flow quantity. |
| **F.QTY** | T50 | The agreed quantity for the flow period. |
| **F.OQTY** | T50 | The original quantity for the flow period. |
| F.OLDNAME | T50 | The old name of the Flow. ( Only to be used if renaming the flow ). |
| F.Udname | T15 | User defined fields for the flow, where ' name ' = the name of the user defined field. |

Example format.

| F.NAME | F.DATE | F.QTY | F.UDname |
|---|---|---|---|
| FLOW-1 | 17/09/2004 | 50 | XYZ |
| FLOW-1 | 24/09/2004 | 75 | XYZ |
| FLOW-1 | 01/10/2004 | 100 | XYZ |
| FLOW-1 | 08/10/2004 | 150 | XYZ |
| FLOW-2 | 24/09/2004 | 20 | ABC |
| FLOW-2 | 01/10/2004 | 50 | ABC |
| FLOW-2 | 08/10/2004 | 150 | ABC |
| FLOW-2 | 15/10/2004 | 150 | ABC |
| FLOW-2 | 22/10/2004 | 150 | ABC |
