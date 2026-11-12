# Reference - Importing Data - FCLinks

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Forecast Links
**Index keywords:** FC Links, FCLinks

---

The data may be imported from a file called FCLINKS.txt or FCLINKS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **FC.ORDER** | T30 | The reference code for the order. |
| **FC.<UDF1>** | T30 | The Forecast UDF, first level of the Forecast Tree. |
| **FC.<UDF2>** | T30 | The Forecast UDF, next level of the Forecast Tree, if applicable. |
| **FC.<UDF....>** | T30 | The Forecast UDF, next level of the Forecast Tree, if applicable. |
| **FC.Product** | T30 | The Proxy Product for the forecast Order. |
| **FC.LINKED** | Boolean | Is this Order Linked to a Forecast, Yes/No. |
| **FC.QUANTITY** | Date | This is the quantity for the Forecast Order. This must total to the order quantity of the Planning Order. |
| FC.PARENTORDER | T30 | This is the Host Order for the order that is getting linked to the forecast. <br> Note: <br> 1. Requires Host Order Substitution. <br> 2. Having this in the import file will not double up the load caused by both Orders after Substitution. |
