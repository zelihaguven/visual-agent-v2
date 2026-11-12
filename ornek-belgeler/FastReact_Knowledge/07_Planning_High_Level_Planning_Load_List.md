# Main Menu - Planning - High Level Planning - Load List

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > High Level Planning > Load List
**Index keywords:** Load List

---

## Load List

*Context: Main Menu > Planning > High Level Planning > Load List › Load List*

The load list will show orders still to be planned. If the user does not have rights to plan orders they will still be able to view the load list.

### "#" new items ("#" units) to load into the "section name" section

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › "#" new items ("#" units) to load into the "section name" section*

### Select order

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Select order*

The Load list contains a list of orders that have still to be planned on the High level planning board. The list contains the following columns of information

**Order Code:** The order reference is preceded with a small rectangle showing the colour (if any) associated with this order. This followed by the order reference itself. There may be several entries in the list for the same order if that order has multiple deliveries. For new orders the colour of this entry will your normal Windows colours (e.g. black on white). However, in systems which have Low level planning, a red order reference will show you that the order had been allocated to a Low level planning board, but that planner had rejected the order.

**Product:** A rectangle showing the colour associated with the Product type for this product, followed by the Product reference for the order.

**Product type:** The product type associated with the product above.

**Customer:** A rectangle showing the colour associated with the Customer followed by the Customer reference.

**Delivery:** The delivery date for this part of the order.

> **Note:** An order can have multiple deliveries.

**Quantity:** The balance to make of this delivery, bearing in mind that an order can be in the load list even if production has already started.

**Description:** This is the description of the Order or the Product. You can decide which you want to show in the planning board configuration.

The Load List can be sorted by clicking on the column headers. All columns, except quantity, are sorted in ascending sequence, whilst the delivery quantity is sorted so that the largest values are at the top of the table.

> **Note:** It is normally easier to plan the large orders before smaller ones.

Double click an order to load it; the load list will close and return to the planning board view.

Multiple orders can also be selected by right clicking on an order and selecting from the options on the pop up menu. See below.

### Load orders

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Load orders*

The right click pop up menu has the following options. When one of these is selected, the load list will highlight the selection. Clicking on the Load orders tab will then close the Load list and return to the planning board view.

**Order set:** All orders that belong to the same order set will be highlighted.

**Linked (::) orders:** All orders that have the same base code (the part up to the double colon separator) will be highlighted.

**Product:** All orders for the selected product will be highlighted.

**Linked (::) products:** All orders that are for the same base product (the part up to the double colon) will be highlighted.

**Autoload selected orders:** This option will only be visible when the option to 'Only allow JIT autoload of Load List orders' is enabled. It will allow the load of the selected order or orders based upon the selection criteria as defined by the above options.

### Auto load

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Auto load*

Once the orders that are to be loaded have been selected, this button will appear. There will be a number on the button. This number will be the number of orders that will be JIT planned.

### Print

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Print*

Click here to print the contents of the load list as a report.

### Low level load list

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Low level load list*

Orders that are in low level load lists will not be visible on the high level planning board (as they are not planned) nor will they be in the High level load list. This list provides a means of locating orders that would otherwise not be visible.

### Configure

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure*

The layout of the Load List dialog can be altered to show User Defined Fields and other useful order and product fields.

#### Order fields

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure › Order fields*

These fields, when checked, will allow the user to see the order details in the load list. See bellow for the field details.

**Code:** This is the order code. When checked this will appear on the Load List display.

**Description:** This is the order description. When checked this will appear on the Load List display.

**Delivery date:** This is the order delivery date. When checked this will appear on the Load List display.

**Quantity:** This is the order quantity. When checked this will appear on the Load List display.

**Reference:** This is the order reference. When checked this will appear on the Load List display.

**Created date:** This is the order created date. When checked this will appear on the Load List display.

**Status:** This is the Order Status. When checked this will appear on the Load List display.

**Next planned group:** This is the group to which the Next 'linked' order is planned on. Available with Complex Routing, Prior/Next and Cascaded planning.

**Host planned group:** This is the group on the 'Host' system that the order is planned on.

**Host start date:** This is the date in the 'Host' system that the order is planned on.

#### Product fields

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure › Product fields*

These fields, when checked, will allow the user to see the product details in the load list. See bellow for the field details.

**Code:** This is the product code. When checked this will appear on the Load List display.

**Description:** This is the product description. When checked this will appear on the Load List display.

**Property:** This is the product property. When checked this will appear on the Load List display. The property will allow the planner to match the order to a particular Planning Group and/or Row.

**Stage:** This is stage (operation) of the planned strip.

#### Order user defined fields

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure › Order user defined fields*

These fields, when checked, will allow the user to see the order User Defined fields in the load list. These fields are created during the set up of the FastReact system.

#### Product user defined fields

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure › Product user defined fields*

These fields, when checked, will allow the user to see the product User Defined fields in the load list. These fields are created during the set up of the FastReact system.

#### Product type fields

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure › Product type fields*

These fields, when checked, will allow the user to see the product type in the load list. See bellow for the field details.

**Code:** This is the product type code. When checked this will appear on the Load List display.

#### Customer fields

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Configure › Customer fields*

These fields, when checked, will allow the user to see the customer in the load list. See bellow for the field details.

**Code:** This is the customer code. When checked this will appear on the Load List display.

**Display sequence:** This is a list of all the above checked fields. The fields in this list can be re-sequenced in order to produce the desired layout on the load list display.

**Sort load list in above sequence:** This check box will sort the load list in the sequence defined in the Display sequence text field.

**Reset defaults (button):** This button will reset the display sequence and all the check boxes to their default settings.

### Autoload

*Context: Main Menu > Planning > High Level Planning > Load List › Load List › Autoload*

FastReact can auto-load orders onto the High Level planning board from the load list, thereby avoiding the manual, drag and drop, process. The rules that FastReact uses are very simplistic in that it will always load orders Just In Time for delivery, allowing for transport to the customer. It will also load orders directly into the group that has been specified for each order. Clearly this will only be relevant in a single section system. FastReact will take no account of group loading against capacity.

Whilst these rules may seem very simplistic for some circumstances they would lend themselves to the planning of sourced orders where the supplier will probably have been decided and supplier capacity is of relatively low concern.

Only orders that have been already assigned to a group can be autoloaded. These orders will have their order code underlined in the load list. Click on the Autoload tab to transfer these orders to the planning board.
