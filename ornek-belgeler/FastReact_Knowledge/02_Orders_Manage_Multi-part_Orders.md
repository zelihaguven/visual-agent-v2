# Main Menu - Orders - Manage Multi-part Orders

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Manage Multi-part Orders
**Index keywords:** Manage Multi, Part Orders

---

## Manage multi-part orders

*Context: Main Menu > Orders > Manage Multi-part Orders › Manage multi-part orders*

The objects that FastReact plans are individual orders. These orders can have a size breakdown and assume that, from a materials calculation point of view, production is completed in line with the size ratio. This is a reasonable assumption, but unfortunately this assumption cannot be extended to production of different colours on an order.

If, for example, an order is to be made in Blue, Green and Red, it might be that only the Red material is available to start, with the other colours not being delivered until some time afterwards. In practice this is not an unusual situation and FastReact must recognise this.

For this reason, where material calculations and planning by colour is required, all FastReact orders must be for a single colour. The purpose of this menu option is to facilitate management of multi-part orders where each part can be for a different colour.

The planner can create a new multi-part order or he/she can edit an existing one.

> **Note:** For the purposes of this document we will assume that the order is for multiple colours, however, you can use the Part for any variant where each variant is to be considered as an element of a higher level order.

### Multi-part orders

*Context: Main Menu > Orders > Manage Multi-part Orders › Manage multi-part orders › Multi-part orders*

**Order base code:** Order codes are formatted as BASECODE::VARIANT where the double colon acts as a separator. This is used extensively throughout FastReact to keep parts of an order together and allow multiple updating and so on. The total length of the base code and part name must be 28 characters or less.

Enter an existing base code to edit or a new base code to create a new multi-part order.

#### Create new order

*Context: Main Menu > Orders > Manage Multi-part Orders › Manage multi-part orders › Multi-part orders › Create new order*

If the Planner enters a base code that does not exist, FastReact will display this page to allow him/her to enter details of the new order.

**Product reference:** Normally a multi-part order will be for a single product. Select a product form the incremental search list.

**Customer:** Normally a multi-part order will be for a single customer. Select a customer from the incremental search list.

**Timetable:** A timetable can be selected for the order or it can be left as '(none)'. This entry will not be visible if Production Event planning is not enabled.

**Copy materials:** Normally the Planner would create multiple orders, each of which might have different material requirements.

For example where each order represents a different colour. In this case it would make no sense to copy materials for each order part. However, it might be that most of the materials are common to each order (e.g. packaging) so the Planner could copy the materials and then edit each part to correct those that are different. FastReact will remember this setting and apply the same for all users.

##### Part table

This is where the individual parts (e.g. colours) of the multi-part order are entered.

**Part name:** Enter the name of the variant. This could be the colour or maybe colour/fit.

> **Note:** The total length of the base code and this entry must not be more than 28 characters.

**Delivery date:** Enter the delivery date for the part. A delivery date must be entered for the first (top) entry in the table, but all of the others entries can be left at their initial value. Unless these dates change FastReact will use the first date for each delivery.

**Delivery quantity:** Enter the quantity that is required for each part. A quantity must be entered for the first (top) entry, but the others can be left at zero. Unless a value is entered FastReact will use the quantity in the top option for each delivery.

**Create and edit first part (button):** The information that is entered here is limited to that which is essential to an order; other values remain uninitialised.

To avoid the problem of uninitialised values, just the first part of the order can be created and FastReact will go directly to the Order Add/Amend dialog so that any other values can be set. When the Order Add/Amend dialog is closed, FastReact will return to the multi-part order dialog.

Clicking on the 'Create all parts', button will create the other parts of the order and the values for the first part that were entered manually will be copied to all of these other parts.

> **Note:** Event progress will not be copied, nor will materials unless above option has been enabled.

**Create all parts (button):** This button will create all of the parts that have been entered on the table.

> **Note:** All order values, for example the selling price, will be at their default settings (i.e. zero) apart from the essential values you have specified above. If the planner chooses 'Create and edit the first part', option then these values will be copied form that first part.

FastReact will now take the planner to the Update order page.

#### Update order

*Context: Main Menu > Orders > Manage Multi-part Orders › Manage multi-part orders › Multi-part orders › Update order*

If a base code that FastReact can find is entered, it will list the various parts of that order. The list will show:-

- The Part name (e.g. the colour),
- The actual colour for that part, if you have defined one,
- The Product (multi-part orders can contain different products),
- The Customer (multi-part orders can contain different customers),
- The Total order quantity across all deliveries,
- The earliest Delivery date,
- The Progress quantity showing how much of each part has been completed,
- A bar chart showing the % of each part that has been completed.

##### Changing order information

Double clicking on any order part will open the Order dialog for that part. From here the order can be amended.

##### Updating production

Right click on an order part to go to the Production Update dialog for that order.

##### Adding new parts

**Part name:** Enter the name of a new part. Remember the overall length limitation of 28 characters.

**Delivery:** Enter a valid delivery date.

**Quantity:** Enter a non zero delivery quantity.

**Add button:** Click the Add button to append this new part to the order. Apart from the details that have just been, entered all other values will be copied from the first order part in the list.
