# Main Menu - Planning - High Level Planning - Grid Style Load List

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > High Level Planning > Grid Style Load List
**Index keywords:** Grid Style Load List

---

With the Use Grid style load list option enabled FastReact offers the User enhanced Sorting and displaying options in the Load List.

## Select orders

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders*

The Load list contains a list of orders that have been planned on the High level planning board,(if the High Level Planning Board is part of the FastReact Licence options) and accepted, by the planner, to the Low Level Board. The list contains the following columns of information:

**Order:** The order reference is preceded with a small rectangle showing the colour (if any) associated with this order. This followed by the order reference itself. There may be several entries in the list for the same order if that order has multiple deliveries. For new orders the colour of this entry will your normal Windows colours (e.g. black on white). However, in systems which have Low level planning, a red order reference will show you that the order had been allocated to a Low level planning board, but that planner had rejected the order.

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

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Load orders*

The right click pop up menu has the following options. When you select one of these the load list will highlight your selection. You can then click on the Load orders tab to close the Load list and return to the planning board. If you are not happy with the selection you can right click on another order and select again.

**Order set:** All orders that belong to the same order set will be highlighted.

**Linked (::) orders:** All orders that have the same base code (the part up to the double colon separator) will be highlighted.

**Product:** All orders for the selected product will be highlighted.

**Linked (::) products:** All orders that are for the same base product (the part up to the double colon) will be highlighted.

Orders can be loaded in the sequence when the Load strips in selected sequence is selected from the Setup - Configure - Planning dialog. This allows for the selecting and planning of multiple orders. This will plan all the selected orders, in order of selection, on one row.

### Print

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Print*

The Load List can be printed.

### Low Level Load List

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Low Level Load List*

At High Level, this tab will list all Orders/Strips in the Low Level Load Lists. This is a static list of Orders/Strips.

### Configure

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure*

The layout of the Load List dialog can be altered to show User Defined Fields and other useful order and product fields.

#### Order fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Order fields*

These fields, when checked, will allow the user to see the order details in the load list. See bellow for the field details.

**Code:** This is the order code. When checked this will appear on the Load List display.

**Description:** This is the order description. When checked this will appear on the Load List display.

**Required date:** This is the date when the planned operation needs to start. When checked this will appear on the Load List display.

**Delivery date:** This is the order delivery date. When checked this will appear on the Load List display.

**Quantity:** This is the order quantity. When checked this will appear on the Load List display.

**Reference:** This is the order reference. When checked this will appear on the Load List display.

**Created date:** This is the order created date. When checked this will appear on the Load List display.

**Status:** This is the status of the Order. When checked this will appear on the Load List display.

**Extended Status:** This is the Extended status of the Order. When checked this will appear on the Load List display.

**Set:** This is the set to which the Order belongs. When checked this will appear on the Load List display.

**Deliver to:** This is the location that the Order is to be delivered to. When checked this will appear on the Load List display.

**Next planned group:** This is the Group of the next planned operation. When checked this will appear on the Load List display.

**Previously planned group:** This is the Group of the previously planned operation. When checked this will appear on the Load List display.

**Host planned group:** This is the Collaborated Group at the Host side that the Order is planned on. When checked this will appear on the Load List display.

**Host start date:** This is the Collaborated start date at the Host side that the Order is planned on. When checked this will appear on the Load List display.

**Host end date:** This is the Collaborated end date at the Host side that the Order is planned on. When checked this will appear on the Load List display.

**Selected stage group:** This is the Group for the selected stage. When checked this will appear on the Load List display.

**Latest Collab site:** This is the Collaborated site that the Order is planned on. When checked this will appear on the Load List display.

#### Product fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Product fields*

These fields, when checked, will allow the user to see the product details in the load list. See bellow for the field details.

**Code:** This is the product code. When checked this will appear on the Load List display.

**Description:** This is the product description. When checked this will appear on the Load List display.

**Property:** This is the product property. When checked this will appear on the Load List display. The property will allow the planner to match the order to a particular Planning Group and/or Row.

**Stage:** This is the stage (operation) of the Order. When checked this will appear on the Load List display.

**Routing valid:** This is 'Yes / No' field to indicate whither the Routing is valid or not. When checked this will appear on the Load List display.

**Route order:** This is a numerical value to indicate the route sequence. When checked this will appear on the Load List display.

#### Order user defined fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Order user defined fields*

These fields, when checked, will allow the user to see the Order User Defined fields in the load list. These fields are created during the set up of the FastReact system.

#### Product user defined fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Product user defined fields*

These fields, when checked, will allow the user to see the Product User Defined fields in the load list. These fields are created during the set up of the FastReact system.

#### Product type fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Product type fields*

These fields, when checked, will allow the user to see the Product Type in the load list. See bellow for the field details.

**Code:** This is the product type code. When checked this will appear on the Load List display.

**Description:** This is the product type description. When checked this will appear on the Load List display.

#### Customer fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Customer fields*

These fields, when checked, will allow the user to see the customer in the load list. See bellow for the field details.

**Code:** This is the customer code. When checked this will appear on the Load List display.

#### Product Type user defined fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Product Type user defined fields*

These fields, when checked, will allow the user to see the Product Type User Defined fields in the load list. These fields are created during the set up of the FastReact system.

#### Customer user defined fields

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Customer user defined fields*

These fields, when checked, will allow the user to see the Customer User Defined fields in the load list. These fields are created during the set up of the FastReact system.

#### Display sequence

*Context: Main Menu > Planning > High Level Planning > Grid Style Load List › Select orders › Configure › Display sequence*

This is a list of all the above checked fields. The fields in this list can be re-sequenced in order to produce the desired layout on the load list display.

**Show load preview image (button):** This option will enable the Image viewer within the Load List. This will be a thumbnail of the image.

**Show where product has been previously made (button):** This option will enable the user to view where Orders with similar products have been made. For an explanation see Suggested Machine/Row.

**Show the planned group for this stage:** In a multiple stage system the user can choose to view the Group in which the Prior or Next planned operation is planned in.

**Reset defaults (button):** This button will reset the display sequence and all the check boxes to their default settings.
