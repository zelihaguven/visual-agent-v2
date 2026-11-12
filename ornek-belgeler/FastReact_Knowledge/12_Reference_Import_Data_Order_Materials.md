# Reference - Importing Data - Order Materials

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Materials
**Index keywords:** Order Materials

---

Orders materials may be imported from a file called OMATS.txt or OMATS.csv.

The following fields may be imported. Essential fields are shown in bold.

The sequence of data in this file is important in that materials for each order should be in blocks as in the example below:

| Order 1 | Material 1 |
|---|---|
| Order 1 | Material 2 |
| Order 1 | Material 3 |
| Order 2 | Material 1 |
| Order 2 | Material 2 |
| Order 2 | Material 3 |

If this convention is followed and the orders are out of sequence then some materials may not be imported correctly.

| Field _ Name | Type | Description |
|---|---|---|
| **N.ORDER** | T30 | The order code. |
| **N.NAME** | T50 | The material reference. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| **N.VALUE** | Float | The usage of this material per unit of the order. |
| N.CAT | T50 | The optional material category. This field is, however, essential if you have duplicated materials on a single order. <br> For example, Warp and Weft are both the same yarn. Warp and Weft in this case must be an existing material in FastReact. |
| N.SIZE | T15 | The size name as defined in FastReact. |
| N.DISABLE | Boolean | Material is valid: <br> 0 = Valid (enabled). <br> 1 = Not valid (disabled). |
