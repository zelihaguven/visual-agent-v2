# Reference - Importing Data - Order Relationships

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Relationships
**Index keywords:** Importing Data, Order Relationships

---

Orders relationships may be imported from a file called RELATE.txt or RELATE.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **O.CODE** | T30 | The order code. |
| O.PRIOR | T30 | The previous order code for the specified order. If an order has many previous orders ( fed by many ) then enter ' -1 '. |
| O.NEXT | T30 | The subsequent order code for the specified order. If an order has many subsequent orders ( feeds many ) then enter ' -1 '. |
| O.PRIORSEC | T30 | This is the prior section for the order. This is required for APS. |
| O.NEXTSEC | T30 | This is the next section for the order. This is required for APS. |
| O.HOST_ORDER | T30 | This is the name of the Order which will be Substituted. |
