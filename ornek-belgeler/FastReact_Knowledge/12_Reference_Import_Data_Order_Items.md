# Reference - Importing Data - Order Items

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Items
**Index keywords:** Order Items

---

Orders items may be imported from a file called ORDITEMS.txt or ORDITEMS.csv.

The following fields may be imported. Essential fields are shown in bold.

The sequence of data in this file is important in that materials for each order should be in blocks as in the example below:

| Order 1 | Order Item 1 |
|---|---|
| Order 1 | Order Item 2 |
| Order 1 | Order Item 3 |
| Order 2 | Order Item 1 |
| Order 2 | Order Item 2 |
| Order 2 | Order Item 3 |

If this convention is not followed and the orders are out of sequence then some order items may not be imported correctly .

| Field Name | Type | Description |
|---|---|---|
| **OI.CODE** | T30 | The order item code. |
| **OI.CUST** | T50 | The item customer. |
| **OI.CUSTREF** | T50 | The item customer reference. |
| **OI.CUSTSTYLE** | T15 | The item customer style. |
| **OI.DUEDATE** | Date | The item due date. |
| **OI.QUANTITY** | Integer | The item quantity. |
| OI.COMMENT | | The item comment. |
