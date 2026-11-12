# Main Menu - Orders - Grid Style Entry

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Grid Style Entry
**Index keywords:** Grid Style Entry

---

## Grid Entry

*Context: Main Menu > Orders > Grid Style Entry › Grid Entry*

The Grid Entry dialog allows the user to view, enter and modify data in a format to which they will be more accustomed to. This dialog is primarily designed to allow users fast data entry and modification.

> **Note:** The Grid Style Entry dialog does not have all the functionality of the Orders Add/Amend dialog and as such may require the user returning to the Add/Amend dialog to alter data.

At present, The Grid Entry functionality only allows for one Delivery and cannot be used with sizes.

### Grid Entry

*Context: Main Menu > Orders > Grid Style Entry › Grid Entry › Grid Entry*

**Find via Name:** This field allows the user to quickly find a desired Product from the list. The use of the '%' filter object greatly enhances this find and filter functionality.

**New (button):** This button will create a new line, in red, at the end of the Product List where a new Product can be entered.

**Copy (button):** This button will copy the currently highlighted Product in the Product List. The copied Product will appear at the end of the list and will be red until a unique Product name is entered and the order 'saved'.

**Delete (button):** This button will delete the currently highlighted Product .

#### Fixed Columns

*Context: Main Menu > Orders > Grid Style Entry › Grid Entry › Grid Entry › Fixed Columns*

This is a list of all the orders within FastReact

**Order name:** This is the name or code of the Order. Fast React Systems advise using a consistent naming convention for orders as this will make future operations much easier. Fast React Systems strongly recommend that spaces are not used as part of the order name and, as such FastReact will strip from the beginning and end of the order name any spaces found.

#### Order Data Columns.

*Context: Main Menu > Orders > Grid Style Entry › Grid Entry › Grid Entry › Order Data Columns.*

**Customer:** Select a customer for this order. To create a new customer click on the small button to the right of this field.

**Delivery date:** The Delivery Date should be the usual date that is used within the business to measure whether an order is on time or late. It could be the ex-factory date, the ex-warehouse date or the date the order is due to arrive at the customer or their local distribution centre.

> **Note:** Grid Entry only allows for one delivery per Order.

**Delivery Qty:** Enter the quantity required for the delivery date. FastReact will not allow an order to be saved unless it has a valid delivery quantity. This quantity must be entered as an integer values.

**Product:** Select a product for this order.

**Order / Product Description:** This is an optional entry of up to 50 characters long. It can be used for a longer description of the order.

If the selected product for the order has a description itself then this will automatically be inserted into this field.

The Order / Product Description can also be configured, using the Configure dialog, to show either the Order Description, the Product Description or both.

**Timetable:** Select a timetable for this order or you can leave this as (none) if the order does not require a timetable.

**Status:** The options are:

- 'Confirmed',
- 'Provisional','
- 'Speculative' and
- 'Transit'.

By default FastReact will mark all new orders 'Confirmed'. This data can be used to distinguish between different types or orders on the plan and for reporting and information purposes. It is also used in complex planning situations (Plan line and APS). The Order name will also appear on the High Level Planning Board in the Status colour of the Order as defined at setup.

**Deliver to:** Normally the final delivery location for an order is derived from the customer details. This default location can be overridden here, so that no matter which location is associated with the customer, FastReact will use selected location. This would be useful where a single customer has a number of delivery locations. With this option the Planner can specify a delivery location for each order.

**Method:** This is the method of transport.

**Plan in Group:** This data is used by APS and JiT to force planning in a single specified group, thereby overriding other Group selection criteria. The group will also be used with the High Level planning Auto load to force loading to a specific group.

**User defined text values:** An Order may require other information that does not have a pre-defined field. FastReact will allow the creation of additional fields.

#### Right Click Functionality

*Context: Main Menu > Orders > Grid Style Entry › Grid Entry › Grid Entry › Right Click Functionality*

The Grid Entry dialog also allows the user to use Right Click Functionality.

[Screenshot: Order Right Click Grid Entry]

**Order Add/Amend (button):** [Screenshot: Order Add Amend]

This option will open the Order Add/Amend dialog.

**Materials (button):** [Screenshot: Order Materials]

This option will open the Material tab on the Order Add/Amend dialog.

**Events (button):** [Screenshot: Order Events]

This option will open the Events tab on the Order Add/Amend dialog.

**User Values (button):** [Screenshot: Order User Values]

This option will open the UDF tab on the Order Add/Amend dialog.

**Progress (button):** [Screenshot: Order Progress]

This option will open the Order Status dialog.

**Notes (button):** [Screenshot: Order Notes]

This option will open the Order Notes dialog.

**Attach Document (button):** [Screenshot: Order Doc Attach]

This option will open the Document Attach dialog.

**Rename (button):** [Screenshot: Order Rename]

This option will open the Rename tab on the Order Add/Amend dialog.
