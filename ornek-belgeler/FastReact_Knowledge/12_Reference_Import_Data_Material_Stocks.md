# Reference - Importing Data - Material Stocks

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Material Stocks
**Index keywords:** Material Stock

---

Material stocks may be imported from a file called MATSTOCK.txt or MATSTOCK.csv.

This import file serves a dual purpose,

- To set-up up new materials.
- To import the stock of a new or existing material.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **M.CODE** | T50 | The unique material code. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| M.DESCRIP | T50 | The material description. |
| M.GROUP | T15 | The group to which this material belongs. The group must exist in FastReact and an error will be raised if an invalid group is found in the import file. A blank group will be accepted however. |
| M.LOCATION | T15 | The location where the material stock is stored. ( This must be a valid location ). <br> This is only required if a stock quantity is being imported. |
| M.SUPPLIER | T15 | The supplier of the specified available stock of the specified material at the specified location. If the supplier is unknown to FastReact it will be created ' on the fly '. This is only required if a stock quantity is being imported. |
| M.AVAIL | Float | The stock quantity. |
| M.SECTION | T15 | The section at which the material is consumed. |
| M.USE_AT | Integer | The operation in the section at which the material is consumed. Only to be used for legacy purposes. Otherwise please see M.OPERATION below. |
| M.OPERATION | Integer | The operation in the section at which the material is consumed. |
| M.PLANNED | Boolean | Indicates whether the specified material is to be planned on the FastReact materials planning board. <br> 0 = Not planned. <br> 1 =planned. <br> NOTE: <br> This requires an additional licence. |
| M.NOT_PHASED | Boolean | Indicates whether materials consumption is phased over the lifetime of the order (the default) or required as one quantity at the start of the order. <br> 0 = phased. <br> 1 = not phased. |
| M.UDname | T15 | The user defined field for a material. ' name ' = the name of the materials user defined field. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| M.SOFT | Boolean | 0 = hard constraint --> Critical Material. <br> 1 = soft constraint --> non Critical Material. |
| M.LEADTIME | Integer | Material lead-time. This is the time from placing and order on a supplier and the material being available for use. |
| M.RECEIVED | Float | Cumulative amount received to-date of the specified material. This is used to update the materials planning board. |
| M.COLT | Integer | Material call off lead time. This is the time that the supplier requires to prepare and transport available goods to your materials warehouse. |
| M.RELEASEAT | Integer | This is the external ID of the operation at which reusable materials are released. |
| M.SIZED | Boolean | This indicates whither or not the material is size specific. <br> 0 = not size specific. <br> 1 = size specific. |
| M.COST | Float | The cost of the Material. |
| M.RESERVATION | T15 | The name of the Reservation against the Order. This will be matched against the Reservation field on the Order. |
| M.IGNORE_STATUS | Boolean | Requires M.SOFT = 1, i.e. a non critical material. This option will ignore the status colours on the strip and if the material with the worst case has this option marked, then it will then have no colour in the material rotations on the planning boards. |
