# Reference - Importing Data - Order WC Override

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Work Content Override
**Index keywords:** Order WC Override

---

Order Work Content Override may be imported from a file called ORDWCOS.txt or ORDWCOS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **WCO.ORDER** | T30 | The unique order code. This field cannot be left blank |
| **WCO.OPN** | INTEGER | The Operation External ID for the operation. |
| **WCO.WC** | INTEGER | The Work Content value that will override the Product Work content for this Order. |

Overrides must be grouped by order code. Existing overrides for an order will be removed, therefore all overrides for a particular order must be present. To remove existing overrides for an order (reset it, so it uses the default values) specify the order without any operations.

| WCO.ORDER | WCO.OPN | WCO.WC |
|---|---|---|
| ORDER 1 | 10 | 1 |
| ORDER 1 | 20 | 2.5 |
| ORDER 2 | | |
| ORDER 3 | 10 | 0 |
