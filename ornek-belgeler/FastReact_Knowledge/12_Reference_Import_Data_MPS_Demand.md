# Reference - Importing Data - MPS Demand

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > MPS Demand
**Index keywords:** MPS Demand

---

Material allocations may be imported from a file called MPSDEMAND.txt or MPSDEMAND.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field _ Name | Type | Description |
|---|---|---|
| **MPS.PRODUCT_NAME** | T30 | FastReact Product Reference. |
| MPS.REFERENCE | T30 | Demand Refrerence (e.g. order code, forecast). |
| **MPS.TYPE** | Integer | 0 = Forecast, 1 = Customer Order. |
| **MPS.DATE** | Date | Date required. |
| **MPS.QUANTITY** | Integer | Quantity required. |
| MPS.CUSTOMER | T30 | FastReact Customer Reference. |
| MPS.COLOUR | T30 | FastReact Colour Name. |
| MPS.SIZENAME | T30 | FastReact Size Name. |
