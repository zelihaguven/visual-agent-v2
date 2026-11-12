# Reference - Importing Data - Customer UDF Exclusions

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Customer UDFs Exclusions
**Index keywords:** Importing Data, Customer UDF Exclusions

---

Customer Profile details may be imported from a file called CUST_UDF_EXCLUSIONS.txt or CUST_UDF_EXCLUSIONS.csv

The following fields may be imported. Essential fields are shown in bold, other fields may be omitted.

| Field Name | Type | Description |
|---|---|---|
| **C.CODE** | T30 | The Customer name. |
| **C.UDFTYPE** | T2 | The 2 character name indicating the type of UDF. <br> PV - Product value. <br> PF - Product financial value. <br> OV - Over value. <br> OF - Order financial value. |
| **C.UDFNAME** | T15 | The name of the UDF. |
| **C.UDFACTIVE** | | Whether the UDF is excluded or not. <br> OFF to indicate the UDF is excluded and hidden for this customer or <br> ON to indicate the UDF is visible for this customer. |
