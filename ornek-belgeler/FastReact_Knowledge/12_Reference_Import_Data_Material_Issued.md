# Reference - Importing Data - Material Issued

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Material Issued
**Index keywords:** Material Issue

---

Material issued quantities may be imported from a file called MATISSUE.txt or MATISSUE.csv.

The following fields may be imported. Essential fields are shown in bold.

Note:

Data in the file MUST be alpha sorted on the CODE column, although the sequence the column takes in the file is unimportant.

This field must also be imported along with the corresponding ORDERS or ORDUPDAT file.

| Field _ Name | Type | Description |
|---|---|---|
| **MATERIAL** | T50 | The raw material reference. |
| **ISSUED** | Float 3 DP | The quantity of material issued to the reference. This value will increase as materials are issued to the PO's. |
| **CODE** | T30 | The Order Grouping reference related to this issued quantity. This field links the Material Issued import file to the Orders file, see , O.GROUPING_CODE on the Orders import file. |

The MATERIAL reference must exactly match the M.CODE reference defined in MATSTOCK.CSV.

The ISSUED quantity must be in the same units of measure as MATSTOCK.CSV and MATSCHED.CSV and OMATS.CSV.

The CODE reference will allow FastReact to dynamically ALLOCATE the "issued" quantity to any orders in the plan matching this reference on a first come first served basis.
