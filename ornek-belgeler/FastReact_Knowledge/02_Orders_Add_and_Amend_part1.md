# Main Menu - Orders - Add and Amend (part 1)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Add and Amend
**Part:** 1 of 2 — sections: Orders - Add/Amend, Define, General, Financial, Sizes, Planning, Materials, Optimise
**Index keywords:** Extended

---

## Orders - Add/Amend

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend*

To be able to use FastReact you must enter your manufacturing, subcontract or sourced, orders. These orders will be planned on various planning boards against your resources (production lines, machines, factories or subcontractors).

### Define

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define*

The Order information entered here can also be changed from within the planning board. Activate the strip menu and select 'Order details'

> **Note:** Security settings can be configured so that sensitive data can be withheld from certain users. For further details please see the documentation relating to Security settings.

**Order reference:** Enter the name or code of the order you want to add or amend, or select an existing order from the incremental search list. Order codes may be up to 30 characters long. We would advise a consistent naming convention for orders as this will make future operation much easier. Fast React Systems strongly recommend that spaces are not used as part of the order name and, as such FastReact will strip from the beginning and end of the order name any spaces found.

> **Note:** Hovering the mouse pointer over the Order Reference field will allow FastReact to pop-out a display box with the Order Name in it. This is particularly useful in systems where long Order names are used.

**Document attach (button):** - [Icon: Document Attach] Attach documents to this order.

Multiple documents can be attached to each order. These documents will be held in a central repository from which FastReact can access them. Click here (see: Main Menu > Setup > Configure > General) for more details.

**Edit order items (button):** - [Icon: Order Line Items] Edit Items for this order.

A main order can be split into one or more Order Items.

**Created:** This is the system date on which the order was created.

**Received:** This is a the date on which the order was received. Normally this will be the same date as the Created date, but in some cases this could differ. The Received date can be manually entered to combat this. This field is required for KPI monitoring.

**Update (button):** This button inserts the product into the database.

**Delete (button):** This button deletes the product from the database.

**Bulk Details (button):** This button will display the Bulked Orders associated with the selected Order.

**Input Schedule (button):** This button will open the Input Schedule dialog.

**Operation Progress (button):** This button bring up the Order Status dialog.

**Consolidated (button):** This button bring up the Order Consolidated Progress dialog.

**Notes (button):** This button brings up the Notes dialog.

#### General

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › General*

**Description:** This is an optional entry of up to 50 characters long. It can be used for a longer description of the order.

If the product you select for the order has a description itself then this will automatically be inserted into this field.

**Product:** Select a product for this order. To create a new product click on the small button to the right of this field.

- [Icon: Products Create Notes] Create or edit the Product.

**Customer:** Select a customer for this order. To create a new customer click on the small button to the right of this field.

- [Icon: Products Create Notes] Create or edit the Customer.

**Timetable:** Select a timetable for this order or you can leave this as (none) if the order does not require a timetable.

**Order set:** This optional entry allows you to enter a 'label' that can be used to link orders together, for example the top and bottom of pyjamas. Different orders could be planned in different factories but you will be able to report these together by sorting by set name.

**Sales Year:** Sales years can optionally be entered. This can be used to sort and filter reports.

**Season:** An order can have a season assigned to it. 12 seasons can be created and reported upon.

**Efficiency:** Efficiencies between 10% and 250% can be entered. This allows the user to define specific production efficiency for the order. This option would normally be used if the production efficiency is expected to be lower (or higher) than typical.

For example, the raw materials may be of poor quality and that production rates will, as a consequence, be lower than normal. When calculating the production time of the orders on the planning board, FastReact will take this efficiency into account in determining the time required to produce the order quantity.

> **Note:** That this is only one of several main areas where expected production efficiencies can be entered.

**Flows (button):** - [Icon: Flows] Flows button.

Flows can be accessed via the Flow button on the Order. This button is only live when the order has a valid Flow attached to it.

**Batch factor (%):** This allows FastReact to scale batches according to the requirements of each order.

For example, a dye vessel can normally hold 600 Kg and, by default, orders would be split into batches of that size. Certain fabrics may be known to crease badly if loaded as full batches so a value entered here allows FastReact to create smaller batches than normal. The converse also applies where larger than normal batches are acceptable.

This field will only be visible if you have the batching option enabled.

**Extended Order Status:** When enabled, this drop down menu will display a list of user defined Status. These Status are defined on the General
- Extended Order Status dialog.

**Prior order:** FastReact (if licensed) allows you to relate orders on the planning board so that attempts to plan an order to start before its Prior order has completed will be highlighted. Enter a Prior order reference here.

**Next order:** FastReact (if licensed) allows you to relate orders on the planning board so that attempts to plan an order so that it completes later than its Next order has started will be highlighted. Enter a Next order reference here.

**Process with:** This option will only be visible when Batches are enabled. This allows the planner to 'group' multiple orders with one planned order. For an explanation please see here.

##### Status

The options are:

- 'Confirmed',
- 'Provisional',
- 'Speculative' and
- 'Transit'.

By default FastReact will mark all new orders 'Confirmed'. This data can be used to distinguish between different types or orders in your plan and for reporting and information purposes. It is also used in complex planning situations (Plan line and APS). The Order name will also appear on the High Level Planning Board in the Status colour of the Order as defined at setup.

##### Reserve

The options are:

- 'None',
- 'Tentative',
- 'Confirmed'

This allows the Order to be flagged as being a Reservation. These options can be imported as well as manually set on the Order.

**Colour (button):** The colour of the order can optionally be defined to represent the actual colour of a dye-lot or the fabric / thread colour. The planning board display can be rotated to view this colour to ensure a logical colour progression on a production line or dye vessel.

**Order is completed:** Check this option to mark the order as completed, irrespective of actual progress. This will apply across all sections in a cascaded system. Orders marked as complete will be hidden on the planning board and in production reports. If an order is uncompleted then any strips relating to that order will be displayed in its original position on the planning board and later strips may be moved back, (replanned).

**Archived:** This check box is available when the Archive module is turned on. This indicates whither or not the Order has been Archived.

> **Note:** This check box is only Live when the Order has been completed.

The act of viewing an already Archived Order in the Order Add/Amend screen will automatically unArchive it.

##### Delivery details

The number of delivery lines visible in FastReact will be limited by the licence.

**Ext.:** Clients can hold an “extension date” against an Order record, this allows the client to “Extend” the Delivery Date without interfering with the Critical Path etc. This check box allows the Planner to enter an extended date and relevant reason note when it is enabled. See Extension dates

**Date:** You must enter at least one delivery date. This should be the usual date that you use in your business to measure whether an order is on time or late. It could be the ex-factory date, the ex-warehouse date or the date the order is due to arrive at your customer or their local distribution centre. FastReact will allow a phased delivery schedule of up to 52 deliveries and delivery dates may be unique or duplicated.

**Quantity:** Enter the quantity required at each delivery date. FastReact will not allow an order to be saved unless it has a valid delivery quantity. These quantities must be entered as integer values, that is you cannot enter a fraction of a unit.

**Reference:** This optional entry allows you to enter a different order reference for each delivery date and quantity specified. This may be used to identify individual sales orders within the overall manufacturing order. This order reference will appear on reports and on the strips on the planning board. The entry maybe up to 15 characters long.

**First:** This is the date of the first delivery.

**Last:** This is the date of the last delivery.

**Total:** This is the total amount to be delivered.

**Contract quantity:** This is a manually entered figure which the user can use to track the Order Contract Quantity.

**Priority:** This optional entry is only used by FastReact APS

**Width:** This value normally has relevance to machine based planning boards only. In order to calculate production times on the planning board FastReact will use the order quantity and the product work content to determine the overall work content for the order. In certain circumstances, however, as production times can be considerably reduced by parallel production.

An example might be a weaving loom of 100 cm width making an order for fabric 33 cm wide. It might be possible for the loom to make 3 widths of fabric across the loom with dividers to split the overall width into 3, or for the fabric to be cut after weaving. In this case the weaving time would be only a third of the normal time.

This value works in conjunction with the Planning board row values of Sections and Section Width.

> **Note:** If this value is zero, but the planning board row has sections and section widths defined then FastReact will assume that the order has the same width as the section and so make only an adjustment for the number of sections.

**Distribute from:** Normally the distribution centre for an order is derived from the customer details. You can override this default group here, so that no matter which distribution centre is associated with the customer, FastReact will use details from the selected group.

**Deliver to:** Normally the final delivery location for an order is derived from the customer details. You can override this default location here, so that no matter which location is associated with the customer, FastReact will use selected location. This would be useful where a single customer has a number of delivery locations. With this option you can specify a delivery location for each order.

**Delivered:** This is the amount of the order that has been delivered. This will be used with multiple deliveries.

**Method:** This is the method of transport.

**Plan in Group:** This data is used by APS and JIT to force planning in a single specified group, thereby overriding other Group selection criteria. The group will also be used with the High Level planning Auto load to force loading to a specific group.

This option is also required in Collaboration when used in conjunction with Host Order Substitution.

**Use route:** Select a route as defined in the setup.

**Earliest start date (button):** - [Icon: Reset Value] Reset the calendar to the default setting.

This is used by APS to optionally prevent orders from being planned earlier than this date.

**Reservation:** - [Icon: Products Create Notes] Create a new Order Reservation.

This option is available when the Reservation Licence option is enabled. This field is a user defined link between the Order and the Material Delivery and/or Material Stock.

**Schedule Offset:** This option allows the planned to define a number of days +/- that you wish FastReact to use when using report fields 'strip offset schedule per \*'. FastReact will take the planned output and report a schedule for the strip x number of days prior to the planned schedule. This can be used to determine when you require new colourings from you client.

**Retain on import:** This option will only be visible if you automatically delete orders in FastReact that are not found in the order import file. If this flag is set then this order will not be deleted if not imported. This will allow you to manually create orders in FastReact that do not exist in the host plan from which imports are derived.

> **Note:** To help identify these orders at a later date a special naming convention should use, otherwise they will get lost amongst the other orders.

**Just in time:** This option is only used in APS.

#### Financial

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Financial*

This tab enables the user to enter financial information relating to your order.

Enter financial values for this order

**Selling Price:** Enter the selling price for the order. By default FastReact will insert the selling price that you will have entered against the product. You can accept this figure or override it on an order by order basis. This will allow you to have a standard price for a product and yet sell that same product at different prices on different orders. This value is used for financial reporting only; it does not affect any other functionality within FastReact.

**Selling cost:** Enter the selling cost for the order, this could include delivery, discounts and commission payments for example. This value is used for financial reporting only; it does not affect any other functionality within FastReact.

#### Sizes

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Sizes*

##### Define size breakdown for this order

If the size option has been enabled, a size breakdown will need to be entered for the order.

**Size:** This will show the names of the sizes that are applicable to the product selected on this order.

**Quantity:** This is the quantity of the order which is required for a particular size, based upon the total order quantity and the figure entered in the ratio column.

**Ratio:** This is the break down of the total order quantity based upon sizes.

If the order quantity changes then FastReact will recalculate the actual quantity per size using your size breakdown.

**Hide sizes with zero quantity (button):** - [Icon] Create or edit the Product, (disabled & enabled).

This button will hide those sizes in the above list that have a zero quantity against them.

#### Planning

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Planning*

##### Planning board

**Planned - (section => planning board):** The planned section name will appear when the order has been planned on either the High Level or Low Level boards.

**Quantity:** This is the quantity of the order per planning board.

**Substitute:** This is the quantity which will be Substituted or, Netted Off, from the selected order.

In the example given above, the Substitute quantity will appear on the Provisional order.

**Host order substitution:** This is the name of the order, selected from a drop down list, from which the Substitution will occur.

Using the previous example, a new Confirmed order will be created and the name of the Provisional order entered in this field. This will Nett Off the Confirmed Order quantity from the Provisional Order quantity.

For a more detailed view to the functionality of Substitution, please see here (see: Functionality > Host Order Substitution).

##### Override planned group by operation

When enabled, operations can be overridden so that they may be planned on groups other than the default group.

**Operation:** This is a list of all operations that the order has to go through in order to produce the finished article.

**Override group:** A new group may be selected from the drop down list. The operation will default to the default group. This default group will be wherever the order is planned.

#### Materials

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Materials*

FastReact offers you the ability to calculate material requirements against planned production. The information within this tab is used to define the materials required and the requirement of each material per item of product.

Material details are defined in the Materials setup menu.

##### Material table

The entry table has the following columns

**Category:** This entry is optional.

Each material requirement is picked from a list of materials shown below the table. Under most circumstances just the material Specification (below) would be required to fully define the requirement. However, there may be times when this is just not enough.

A good example would be where a weaver might require the same yarn in his warp and his weft. You could enter the yarn once and also the combined requirement for both warp and weft as a single usage value. This would be fine in the calculation of total requirements bout it would be inadequate in determining the timing of the requirement. This is because weft yarn will be consumed over the production period of the order whilst the warp yarn will all be required before the order can start in weaving. To overcome this problem you can create two materials, one called 'WARP' and the other called 'WEFT' and set the Phased flag on each accordingly. When FastReact performs materials calculations it will use the settings for any materials in the Category column to override the settings in the Specification column

**Specification:** Select the material specification from the list of materials below.

**Disable:** When enabled, this option will allow the user to select and deselect materials which will be used on the Order BoM. This field is also importable.

**Reservation:** This is the Reservation identifier that is used to link the material being reserved to th Order that the material is reserved for.

**Usage/Sizes:** The next columns allow you to enter a usage value, that is the quantity of material per item of this order. If you have the size option enabled then you can enter the materials required for each size in your size that you have used in your size breakdown. This allows you to use different materials per size or just different quantities of the same materials per size.

> **Note:** The materials defined for the product may be seen at the top of the list, however, as these are initially hidden, you will need to scroll further up the list.

**Fill across (button):** - [Icon: Products Show Progress Notes] Fill values across.

This button will, when clicked, automatically fill in the Usage/Sizes fields with the value entered in the first highlighted field on the particular row.

**Move (button):** - [Icon: Left Right Move] Move between sizes values on the Material sizes table.

**Search for materials:** If you have a large number of materials then FastReact can help find the one you want by means of a search list. Enter the first few characters of the material you want and FastReact will filter the list for you

##### Materials list

To add materials to the specification list you just drag them with the mouse into the appropriate column. To remove a material just set its usage to zero.

**Do not mix materials from different suppliers:** This option is not available unless you have materials calculations within the terms of your licence

Materials may be purchased from a number of different suppliers. When calculating materials availability against requirements, FastReact will normally add together the stock and delivery from all suppliers. If, for any reason, you would prefer that each product be satisfied from a single supplier then enable this option.

**Do not mix alternative materials.:** FastReact will allow you to specify up to 9 alternatives for each material required on the product. This information can only be imported, not manually entered. When FastReact performs materials calculations of availability against requirements it would normally try to satisfy a requirement from a single material. Failing this it will top up availability from alternatives, if any. Enable this option if you want to ensure that a product is only made from a single material of the alternatives

> **Note:** If 'Do not mix materials from different suppliers' is switched on this option is automatically switched on.

**Operations view (button):** - [Icon: Products Show Progress Notes] Toggle to the Materials consumed at dialog.

This button will switch from the Materials view to the Materials consumed at view.

#### Optimise

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Optimise*

This tab will only be accessible if, during set up you have switched on optimise loading. This is done via the Setup
- Configure - Planning menu option.

Certain constraints can be set-up for each resource (e.g. planning board row or group) and then for each Order values can defined which FastReact will use to assess the suitability of that Order on that resource.

For example. A 300 kg dye vessel can only accept orders with a weight below 300 kg and for reasons of efficiency it may be restricted to Orders with a minimum weight of 250 kg. If the optimise value for the Order is 235kgs (that is outside the acceptable range), FastReact can one of do two things. It can prevent you from loading this order on this machine, or it can warn you of an issue by turning the text background dark grey.

This option is normally used on systems that are planning machines rather than operators.

**Factor:** This list shows the pre-defined optimising factors set-up under Setup
- Production - Optimise Loading Factors.

**Value:** Enter a numeric (integer) value for each factor on this order.

#### Operations

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Operations*

This licence option allows the Re-processing of an Order, for example a Dye batch. A rejected Batch may need to go through the Dye vat multiple times. In addition, the cycle times may change. To model this scenario it is necessary to amend the routing.
