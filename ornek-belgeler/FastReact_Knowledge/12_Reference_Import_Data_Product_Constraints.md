# Reference - Importing Data - Product Constraints

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Product Constraints
**Index keywords:** Product Constraints

---

Attended Time details may be imported from a file called PROD_CONSTRAINTS.txt or PROD_CONSTRAINTS.csv

The following fields may be imported. Essential fields are shown in bold, other fields may be omitted.

| Field Name | Type | Description |
|---|---|---|
| **C.PRODUCT_NAME** | T15 | The name of the Product. |
| **C.CONSTRAINT_NAME** | T15 | The name of the Constraint. |
| C.SIZE | T15 | The size that the constrain applied to. |
| C.USAGE | Integer | The material usage for the product. |

> **Note:** A Usage value of "0" or not present will delete the Constraint.
