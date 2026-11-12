# Reference - Importing Data - Product Operations

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Product Operations
**Index keywords:** Product Operations

---

Product Operations may be imported from a file called PRODOPNS.txt or PRODOPNS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **P.CODE** | T30 | The product code. |
| **P.OPN** | Date | The product operation external id. |
| **P.WC** | Integer | The product work content. |
| P.NEXTWC | Integer | The "Next" work content value. <br> Note: this is a required field when the "Now and Next" functionality is Licenced. |
| P.NEXTDATE | Date | The "Next" date that the "Next" work content will start from. <br> Note: this is a required field when the "Now and Next" functionality is Licenced. |
| P.CM | Integer | The product change minutes. |
| P.ST | Integer | The product standing time. |
| P.FACTOR | Integer | The product conversion factor. |
| P.ROUTE | Float | The product route. This will default to the first route if there are no routes defined. |
| P.SEQUENCE | Complex | The sequence number the operation appears in the Routing. |
| P.DESCRIPTOR | T30 | The Descriptor Code/Name |

The style MUST already exist within FastReact, either imported as a Product.csv / Product.txt file or manually created via the Products Add/Amend dialog.

Example format:

Example 1:

| P.CODE | P.OPN | P.WC | P.CM | P.ST | P.FACTOR |
|---|---|---|---|---|---|
| Product 1 | 10 | 1.45 | 60 | 0 | 0 |
| Product 1 | 22 | 2.78 | 0 | 1 | 0 |
| Product 1 | 20 | 3.80 | 0 | 1 | 0 |
| Product 1 | 28 | 2.60 | 60 | 0 | 0 |
| Product 1 | 26 | 90.56 | 0 | 1 | 0.75 |
| Product 1 | 32 | 100.50 | 0 | 0 | 0 |
| Product 1 | 94 | 1.00 | 0 | 1 | 0 |

Example format: This example shows the import file with the "Now and Next" licence option enabled. If there is no NEXTWC and NEXTDATE then 0 and 01/01/2000 can be used.

Example 2:

| P.CODE | P.OPN | P.WC | P.NEXTWC | P.NEXTDATE | P.CM | P.ST | P.FACTOR |
|---|---|---|---|---|---|---|---|
| Product 2 | 26 | 90.56 | 91 | 13/06/2015 | 0 | 1 | 0.75 |
| Product 2 | 32 | 100.50 | 91 | 13/06/2015 | 0 | 0 | 0 |
| Product 2 | 94 | 1 | 1 | 13/06/2015 | 0 | 1 | 0 |
| Product 2 | 20 | 3.80 | 4 | 13/06/2015 | 0 | 1 | 0 |
| Product 2 | 28 | 2.60 | 3 | 13/06/2015 | 60 | 0 | 0 |
| Product 2 | 10 | 1.45 | 2 | 13/06/2015 | 60 | 0 | 0 |
| Product 2 | 00 | 2.78 | 3 | 13/06/2015 | 0 | 1 | 0 |

With the above two examples it is the sequence of the P.OPN field which determines the manufacturing sequence of this style.
