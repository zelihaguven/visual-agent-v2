# Reference - Importing Data - Product Types

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Product Types
**Index keywords:** Importing Data, Product Types

---

Product types may be imported from a file called PRODTYPE.txt or PRODTYPE.csv.

The following fields may be imported. Essential fields are shown in bold:

| Field Name | Type | Description |
|---|---|---|
| **T.CODE** | T15 | The unique product type code. This field cannot be left blank. |
| T^WC: n | Float | Work content by operation. <br> ' n ' = the external ID for the operation. |
| T^CM: n | Float | Change minutes by operation <br> ' n ' = the external ID for the operation. |
| T.DESCRIP | T50 | Product type description. |
| T.SPRICE | Float | Product type selling price. |
| T.LABCOST | Float | Product type labour cost. |
| T.MATCOST | Float | Product type material cost. |
| T.OTHCOST | Float | Product type other ( material ) cost. |
| T.REJPC | Float | Product type reject percent. |
| T.COLOUR | Integer | Strip colour in Windows RGB format. If this value is omitted, FastReact will default this colour to White. |

All operations that are imported will default to having a 'Used' status. This can be turned off in the Product Type definition option. See Main menu - Setup - General - Product types - Operations tab.
