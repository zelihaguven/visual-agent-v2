# Reference - Importing Data - Product Sizes

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Product Sizes
**Index keywords:** Product Size

---

Products may be imported from a file called PRODSIZE.txt or PRODSIZE.csv. This import file works with the "Allow import of data from multiple files" option.

The following fields may be imported. Essential fields are shown in bold. If the P.STOCK and P.MIN_STOCK. fields are present in the file then the stock data will be updated else it will not be changed.

If the Size on the PRODSIZE import file does not exist FastReact will create it during the import.

> **Note:-:** The P.STOCK and P.MIN_STOCK. fields cannot be updated independently, it is either both or none.

| Field Name | Type | Description |
|---|---|---|
| **P.CODE** | T30 | The unique product code. This field cannot be left blank. |
| **P.SIZENAME** | T25 | Multiple sizes to be available on this product. |
| P.STOCK | Integer | The stock qty per size. |
| P.MIN_STOCK | Integer | The target stock FastReact will hold after running MPS. |

For example,

| P.CODE | P.SIZENAME |
|---|---|
| Product1 | L |
| Product1 | M |
| Product1 | S |
| Product1 | XL |
| Product2 | L |
| Product2 | M |
| Product2 | S |
| Product2 | XL |

For this import file FastReact will warn the user if:

- Code blank or not found in FastReact,
- Size name blank or not found in FastReact,
- Size name duplicated
