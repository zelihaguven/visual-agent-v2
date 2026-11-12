# Reference - Importing Data - Document Attach

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Document Attach
**Index keywords:** Document Attach

---

Attached documents for both Orders and Products may be imported. To be more precise, it is not the attached document itself which is imported but the Network path to the location of that document that is imported.

The data may be imported from a file called DATTACH.txt or DATTACH.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **DA.CODE** | T30 | The reference code for the order or product. |
| **DA.TYPE** | T1 | Pass a ' O ' if the code above refers to an Order or a ' P ' if it refers to a Product. |
| **DA.FILENAME** | T255 | The name of the file to be attached. |
| **DA.FILEPATH** | T255 | The location of the file to be attached. |
| DA.PUBLIC | Boolean | Whither the above file is for public viewing or not. Pass a ‘ 1 ’ for Public and a ‘ 0 ’ for Not Public. |
