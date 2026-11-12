# Reference - Importing Data - Order Update

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Update

---

Orders may be imported from a file called ORDUPDAT.txt or ORDUPDAT.csv.

The following fields may be imported. Essential fields are shown in bold.

This type of import will only change an existing Order it will not create a new Order. All that is needed in the file would be the O.CODE and any other field that requires changing. There is no need to include any other field.

> **Note:** If importing a change to either a Delivery Date or a Delivery Quantity, then BOTH these fields must be included in the import file.

> **Note:** When importing the Expected Date, the Completed Date column must also be included, (O^ED or O^EDONE). The Completed Date may be blank if this Event is not actually completed.

| Field Name | Type | Description |
|---|---|---|
| (On General Tab) | | |
| **O.CODE** | T30 | The unique order code. This field cannot be left blank |
| O.PROD | T30 | The product associated with this order. This field must contain a valid FastReact product else the order will be rejected. |
| O.CUST | T15 | The customer associated with this order. This field must contain a valid FastReact customer else the order will be rejected. |
| O^DD: n | Date | A list of delivery dates where ' n ' is a sequential number to define multiple deliveries on an order. This number must be sequential starting from 1. <br> Note: <br> If importing a change to either a Delivery Date or a Delivery Quantity, then BOTH these fields must be included in the import file. |
| O^DQ: n | Integer | A list of delivery quantities. This list must match the delivery date list above and ' n ' is a sequential number to define multiple deliveries on an order. This number must be sequential starting from 1. <br> Note: <br> If importing a change to either a Delivery Date or a Delivery Quantity, then BOTH these fields must be included in the import file. |
| O^DR: n | T15 | An optional list of short descriptions for each delivery where ' n ' is a sequential number to define multiple deliveries on an order. This number must be sequential starting from 1. |
| O.STATUS | T1 | F = Confirmed order <br> P = Provisional order <br> S = Speculative order <br> T = Transit order <br> X or 9 = The order will be marked as complete or deleted depending on your Import settings. |
| O.DESCRIP | T50 | Order description. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| O.TIME | T15 | The production timetable associated with this order. If the field is populated then it must contain a valid FastReact timetable else the order will be rejected. If not populated then the existing timetable on the order will be retained. |
| O.COLOUR | Integer | Order colour for this Order. |
| O.APGROUP | T15 | This must be a valid FastReact planning group. It is used in JIT auto-planning to specify the group into which the order is to be loaded. It is also used by APS to force an order to be loaded into a specific group. |
| O.SET | Integer | The order set that this order belongs to. The order set must exist in FastReact. |
| O.FLOW | T30 | The flow name that the order belongs to. The flow name must exist in FastReact. |
| O.DELIVERED | Integer | The quantity that has been delivered on this order. |
| O.ROUTE | T15 | This is the Route on the order. |
| O.SALES_SEASON | T15 | This is a manually entered field for the season in which the order is in. |
| O.SALES_YEAR | Date | The year in which the order is based. |
| O.RECEIVED_DATE | Date | This is the date that the order was received. |
| O.EX_STATUS | T15 | When Extended Order Status has been enabled this field will import the Extended Order Status. To import this field, the Unique ID must be used. |
| O.CONTRACT_QTY | T15 | When Contract Quantity has been enabled this field will allow the importing of the Contract Qty. |
| O.WIDTH | Integer | The width value for the order. |
| O.EFFY | Integer | The expected efficiency of the order compared to the normal efficiency. This will default to 100% if the field is skipped. |
| O.BATCHFAC | Integer | Percentage or factor of increase or decrease of the batch. |
| O.COMPLETE | Integer | Order is complete: <br> 0 = Not completed. <br> 1 = Completed. |

*(table continued)*

| Field Name | Type | Description |
|---|---|---|
| O.JIT | Integer | Used for APS. |
| O.PRIORITY | Integer | The order priority for APS ( range -10 to +10 ). |
| O.TRANS_OVERRIDE | T15 | The method of transport as defined on the Order. |
| O.DELIVLOC | T15 | The location where the Order will be delivered. |
| O.RESERVE_STATUS | Integer | This status is enabled via the FRS system login under the Setup dialog option it is visible on the Order Add/Amend dialog under the " Reserve " status group. <br> 1 = Tentative, <br> 2 = Confirmed, <br> anything else = none. |
| O.RESERVATION | T15 | The name of the Reservation against the Order. This will be matched against the Reservation field on the Material Stock file and/or Material Schedule file. |
| O^EXDD: n | Date | A list of extended dates where ' n ' is a sequential number to define multiple extended dates on an order. This number must be sequential starting from 1. <br> Note: <br> If importing an Extended Delivery Date then the Delivery Date and the Delivery Quantity fields must BOTH be included in the import file. |
| O^EXDR: n | T15 | An optional list of short descriptions for each extended delivery where ' n ' is a sequential number to define multiple extended dates on an order. This number must be sequential starting from 1. |
| O.ARCHIVED | Integer | Order is archived: <br> 0 = Not archived. <br> 1 = Archived. |
| (On Financial Tab) | | |
| O.SPRICE | Float | The selling price for the order. |
| O.SCOST | Float | The selling costs for the order. |
| O.Fv" name" | Float | User defined Financial fields for the order, where ' name ' = the name of the user defined financial field. |
| (On Size Tab) | | |
| O^SIZENAME: n | T25 | The sizes to be used on this order. Multiple sizes are differentiated with the ' n ' suffix which is a sequential number from 1 upwards. Sizes must exist and FastReact will raise an error if an imported size does not exist. |
| O^SIZERATIO: n | Integer | The quantity of the total order for each size. This value can be actual order items ort can be a ratio of one size to another. The ‘ n ’ suffix is used to link the size name above to the size ratio. |
| (On Planning Tab) | | |
| O^SPB:" section " | T15 | The planning board to which this order is to be allocated where " section name " is the name defined within FastReact. <br> Note: <br> Once an order has been allocated to a planning board it cannot be reallocated. |
| (On Materials Tab) | | |
| O^MU: n | Float | Material usage per order unit of the product. Where ' n ' is a sequential number ( 1 to many ) to define multiple materials on an order. |
| O^MN: n | T50 | Material name/specification. Where ' n ' is a sequential number ( 1 to many ) to define multiple materials on an order. |
| O^MC: n | T50 | Material category. ' n ' is a sequential number to define. multiple materials on an order. |
| O^ML: n | Integer | Material operation where ' n ' = the operation external reference. |
| O.NMS | Integer | Whether materials can include mixed suppliers: <br> 0 = Suppliers can be mixed. <br> 1 = Suppliers cannot be mixed. |
| O.NMA | T15 | Whether alternative materials can be mixed alternatives: <br> 0 = Alternatives can be mixed. <br> 1 = Alternatives cannot be mixed. |

*(table continued)*

| Field Name | Type | Description |
|---|---|---|
| O^MUD: n | T15 | Material user defined field where ' n ' is the external reference for the user defined field. |
| (On Optimise Tab) | | |
| O^OV: n | Integer | The optimise values for the order where ' n ' is the external reference for the optimise factor. |
| (On Events Tab) | | |
| O.EVBASE | Date | Event base date, critical path event dates can be linked to this date. |
| O^ED: n | Date | The actual completion date of an order related event where ' n ' is the external reference for an event. OR…. |
| O^EDONE: n | Date | The actual completion date of an order related event where ' n ' is the external reference for an event. This import field is used with Collaborative Planning. |
| Note: <br> O^ED and O^EDONE import the same figure but are NOT interchangeable. O^ED will not work with Collaborative Planning. | | |
| O^XD: n | Date | The expected date of an order related event where ' n ' is the external reference for an event. <br> Note: <br> When importing the expected date, the completed date column must also be included (O^ED or O^EDONE). The completed date may be blank if this Event is not actually completed. |
| O.APBD | Date | APS base date. Orders will not be planned earlier than this date during an APS run. |
| O.TRANSMETHOD | T15 | Transport method for the order - This is normally used with Critical Path only planning systems. This is only visible if an event is set to Release Date. |
| O.DC | T15 | The DC name for the order - This is normally used with Critical Path only planning systems. This is only visible if an event is set to Release Date. |
| O.ORIGINATE | T15 | The location of the material source - This is normally used with Critical Path only planning systems. This is only visible if an event is set to Release Date. |
| (On User Value Tab) | | |
| O.Ud" name" | T15 | User defined fields for the order, where ' name ' = the name of the user defined field. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| O.STOCK_OUT_DATE | Date | Warning date shown visually on the Planning Board by Red hashing. Commonly used to indicate when stock will run out for specific orders. |
| (On Property Tab) | | |
| O.PROPS | T15 | Order property for resource matching - Used for APS only. |
| (Other import fields) | | |
| O^OMD: n | Integer | The Move days associated with each operation where ' n ' = External reference for each operation. |
| O^RQ: n | Integer | The cumulative reject quantity of the order that has passed through your operations where ' n ' = External reference for each operation. |
| O^PQ: n | Integer | The cumulative quantity of the order that has passed through your operations where ' n ' = External reference for each operation. |
| O.OLDCODE | T30 | If the code passed in this field is an existing FastReact order then this order will be renamed to the code passed in the field O.CODE. |
| O.INHERIT_FROM | T30 | The name of the order from which the details will be inherited from. |
| O.CPCOPY | T30 | This will copy the Critical Path from an existing order to the imported order. |

*(table continued)*

| Field Name | Type | Description |
|---|---|---|
| O.BULK | Integer | Used as part of the bulk order processing unit. This is an internal setting within FastReact. |
| O.GROUPING_CODE | T50 | This field is used in conjunction with the Material Issued import file and links the Order or Group of Orders to the CODE on the Material Issued file. |
