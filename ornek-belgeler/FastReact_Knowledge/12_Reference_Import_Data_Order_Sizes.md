# Reference - Importing Data - Order Sizes

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Sizes
**Index keywords:** Order Sizes

---

Products may be imported from a file called ORDSIZE.txt or ORDSIZE.csv. This import file works with the "Allow import of data from multiple files" option.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **O.CODE** | T30 | The unique order code. This field cannot be left blank |
| **O.SIZENAME** | T25 | The sizes to be used on this order. |
| **O.SIZERATIO** | Integer | The quantity of the total order for each size. |

For example,

| O.CODE | O.SIZENAME | O.SIZERATIO |
|---|---|---|
| Order1 | L | 500 |
| Order1 | M | 200 |
| Order1 | S | 300 |
| Order1 | XL | 500 |
| Order2 | L | 200 |
| Order2 | M | 300 |
| Order2 | S | 600 |
| Order2 | XL | 200 |

For this import file FastReact will warn the user if:

- Code blank or not found in FastReact,
- Size name blank or not found in FastReact,
- Size name duplicated
- Bulk Order processing licenced,
- The sum of the size ratios for an order doesn't equal the total order qty.

This file will also allow the importing of a ratio for a size that is not valid on the order's product.
