# Reference - Importing Data - Material Schedules

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Material Schedules
**Index keywords:** Material Schedules

---

Material schedules may be imported from a file called MATSCHED.txt or MATSCHED.csv.

If importing the same material for multiple suppliers and/or multiple locations the import file must be sorted in the sequence M.CODE, M.SUPPLIER, M.LOCATION. otherwise data may be missed.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **M.CODE** | T50 | The unique material code. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information |
| **M.DELDATE** | Date | The delivery date of the specified material. |
| **M.DELQTY** | Float | The delivery quantity expected on the specified date. |
| M.SUPPLIER | T15 | The supplier of the specified material. If the supplier is not known to FastReact it will be created ' on the fly '. |
| M.LOCATION | T15 | The location where the material stock is stored. ( This must be a valid location ). |
| M.INTRANSIT | Boolean | Indicates whether the specified material is in transit or not. <br> 0 = Not in transit. <br> 1 = In transit |
| M.RESERVATION | T15 | The name of the Reservation against the Order. This will be matched against the Reservation field on the Order. |
| M.POREF | T15 | The Material PO reference as defined on the Deliveries Expected dialog. |

> **Note:**

> **Note:** Whilst FastReact will store details of overdue deliveries it will ignore these in most circumstances. It is the responsibility of the host plan to ensure that delivery information is valid.
