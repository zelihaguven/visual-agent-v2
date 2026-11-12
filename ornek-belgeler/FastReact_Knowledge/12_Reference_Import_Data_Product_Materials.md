# Reference - Importing Data - Product Materials

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Product Materials
**Index keywords:** Product Materials

---

Product materials may be imported from a file called PMATS.txt or PMATS.csv.

The following fields may be imported. Essential fields are shown in bold.

The sequence of data in this file is important in that materials for each product should be in blocks as in the example below:

| Product 1 | | Material 1 |
|---|---|---|
| Product 1 | | Material 2 |
| Product 1 | | Material 3 |
| Product 2 | | Material 1 |
| Product 2 | | Material 2 |
| Product 2 | | Material 3 |

If you do not follow this convention and have products out of sequence then some materials will not be correctly imported.

| Field Name | Type | Description |
|---|---|---|
| **N.PRODUCT** | T30 | The product code. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| **N.NAME** | T50 | The material reference. |
| **N.VALUE** | Float | The usage of this material per unit of the product. |
| N.CAT | T50 | The optional material category. This field is, however, essential if you have duplicated materials on a single product. <br> For example, Warp and Weft are both the same yarn. Warp and Weft in this case must be an existing material in FastReact. |
| N.SIZE | T15 | The size name as defined in FastReact. |
| N.DISABLE | Integer | Material is valid: <br> 0 = Valid (enabled). <br> 1 = Not valid (disabled). |
