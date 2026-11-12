# Main Menu - Planning - Low Level Planning - Load List

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > Low Level Planning > Load List
**Index keywords:** Load List

---

## Load list

*Context: Main Menu > Planning > Low Level Planning > Load List › Load list*

The load list will show orders still to be planned. If the user does not have rights to plan orders they will still be able to view the load list.

### Select orders

*Context: Main Menu > Planning > Low Level Planning > Load List › Load list › Select orders*

The Load list contains a list of orders that have been planned on the High level planning board,(if the High Level Planning Board is part of the FastReact Licence options) and accepted, by the planner, to the Low Level Board. The list contains the following columns of information:

**Order:** The order reference is preceded with a small rectangle showing the colour (if any) associated with this order. This followed by the order reference itself. There may be several entries in the list for the same order if that order has multiple deliveries. For new orders the colour of this entry will your normal Windows colours (e.g. black on white). However, in systems which have Low level planning, a red order reference will show you that the order had been allocated to a Low level planning board, but that planner had rejected the order.

**Product:** A rectangle showing the colour associated with the Product type for this product, followed by the Product reference for the order.

**Product type:** The product type associated with the product above.

**Customer:** A rectangle showing the colour associated with the Customer followed by the Customer reference.

**Delivery:** The delivery date for this part of the order.

> **Note:** An order can have multiple deliveries.

**Quantity:** The balance to make of this delivery, bearing in mind that an order can be in the load list even if production has already started.

**Description:** This is the description of the Order or the Product. You can decide which you want to show in the planning board configuration.

**Planning row:** This column will only appear when the option, "Autoload by Planning Row" is enabled and will only work with the Low Level Grid Style load list. Selection of a planning row is done by clicking the Planning row cell and selecting a row from the drop down. One or more orders can be planned at the same time, however when 'Load planned orders' is clicked, an highlighted orders will be ignored and only orders with planning rows will be planned. The name of planning row may also be entered by typing in the cell. Orders are sorted by delivery date and are planned to each selected planning row in this order.

The Load List can be sorted by clicking on the column headers. All columns, except quantity, are sorted in ascending sequence, whilst the delivery quantity is sorted so that the largest values are at the top of the table.

> **Note:** It is normally easier to plan the large orders before smaller ones.

Double click an order to load it; the load list will close and return to the planning board view.

Multiple orders can also be selected by right clicking on an order and selecting from the options on the pop up menu. See below.

##### Production History

Once enabled this functionality allows the Planner to view where previous updates have taken place. For more explanation on this functionality please see here (see: Functionality > Suggested Machine/Row).

**Date:** This is the date of the production update.

**Group:** This is the Group on which the update was done.

**Row:** This is the Row on which the update was done.

**Quantity:** This is the Update quantity based on Row, Group and Date.

### Load orders

*Context: Main Menu > Planning > Low Level Planning > Load List › Load list › Load orders*

The right click pop up menu has the following options. When you select one of these the load list will highlight your selection. You can then click on the Load orders tab to close the Load list and return to the planning board. If you are not happy with the selection you can right click on another order and select again.

**Order set:** All orders that belong to the same order set will be highlighted.

**Linked (::) orders:** All orders that have the same base code (the part up to the double colon separator) will be highlighted.

**Product:** All orders for the selected product will be highlighted.

**Linked (::) products:** All orders that are for the same base product (the part up to the double colon) will be highlighted.

Orders can be loaded in the sequence when the Load strips in selected sequence is selected from the Setup - Configure - Planning dialog. This allows for the selecting and planning of multiple orders. This will plan all the selected orders, in order of selection, on one row.

#### Print

*Context: Main Menu > Planning > Low Level Planning > Load List › Load list › Load orders › Print*

The Load List can be printed.

#### Configure

*Context: Main Menu > Planning > Low Level Planning > Load List › Load list › Load orders › Configure*

The layout of the Load List dialog can be altered to show User Defined Fields and other useful order and product fields.

###### Order fields

These fields, when checked, will allow the user to see the order details in the load list. See bellow for the field details.

**Code:** This is the order code. When checked this will appear on the Load List display.

**Description:** This is the order description. When checked this will appear on the Load List display.

**Delivery date:** This is the order delivery date. When checked this will appear on the Load List display.

**Quantity:** This is the order quantity. When checked this will appear on the Load List display.

**Reference:** This is the order reference. When checked this will appear on the Load List display.

**Created date:** This is the order created date. When checked this will appear on the Load List display.

**Status:** This is the order status. When checked this will appear on the Load List display.

**Extended status:** This is the order Extended status. When checked this will appear on the Load List display.

**Deliver to:** This is the order Deliver to. When checked this will appear on the Load List display.

**High level group:** This is the order HL Group. When checked this will appear on the Load List display.

**High level start date:** This is the order HL start date. When checked this will appear on the Load List display.

**Previously planned:** This is a Yes/No field to highlight previously planned strips. When checked this will appear on the Load List display.

**Host planned group:** This is used in collaboration setups to name the Host systems group. When checked this will appear on the Load List display.

**Host start date:** This is the start date that the order is planned on at a Host collaborative system. When checked this will appear on the Load List display.

**Host end date:** This is the end date that the order is planned on at a Host collaborative system. When checked this will appear on the Load List display.

**Planned group:** This is the group to which the order has been assigned. The order is assigned to a group via the Orders Add/Amend dialog. This option should only be used when JIT loading is enabled. When checked this will appear on the Load List display.

**Start date:** This is the start date to which the order has been assigned. The order is assigned a start date via the Orders Add/Amend dialog. This option should only be used when JIT loading is enabled. When checked this will appear on the Load List display.

###### Product fields

These fields, when checked, will allow the user to see the product details in the load list. See bellow for the field details.

**Code:** This is the product code. When checked this will appear on the Load List display.

**Description:** This is the product description. When checked this will appear on the Load List display.

**Property:** This is the product property. When checked this will appear on the Load List display. The property will allow the planner to match the order to a particular Planning Group and/or Row.

###### Order user defined fields

These fields, when checked, will allow the user to see the Order User Defined fields in the load list. These fields are created during the set up of the FastReact system.

###### Product user defined fields

These fields, when checked, will allow the user to see the Product User Defined fields in the load list. These fields are created during the set up of the FastReact system.

###### Product type fields

These fields, when checked, will allow the user to see the Product Type in the load list. See bellow for the field details.

**Code:** This is the product type code. When checked this will appear on the Load List display.

###### Customer fields

These fields, when checked, will allow the user to see the customer in the load list. See bellow for the field details.

**Code:** This is the customer code. When checked this will appear on the Load List display.

###### Display sequence

This is a list of all the above checked fields. The fields in this list can be re-sequenced in order to produce the desired layout on the load list display.

###### Product Type user defined fields

These fields, when checked, will allow the user to see the Product Type User Defined fields in the load list. These fields are created during the set up of the FastReact system.

###### Customer user defined fields

These fields, when checked, will allow the user to see the Customer User Defined fields in the load list. These fields are created during the set up of the FastReact system.

**Show where product has been previously made:** This option will enable the user to view where Orders with similar products have been made. For an explanation see Suggested Machine/Row.

**Reset defaults (button):** This button will reset the display sequence and all the check boxes to their default settings.

**Show the planned group for this stage:** In a multiple stage system the user can choose to view the Group in which the Prior or Next planned operation is planned in.
