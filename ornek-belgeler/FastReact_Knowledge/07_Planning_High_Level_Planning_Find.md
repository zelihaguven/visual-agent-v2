# Main Menu - Planning - High Level Planning - Find

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > High Level Planning > Find

---

## Find

*Context: Main Menu > Planning > High Level Planning > Find › Find*

This option allows the planner to find information on the planning board. It does this by selecting a subset of orders, displaying just those that are required.

### Find

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find*

**Find (button):** This button will close the dialog and filter the planning board display to show just those orders that match the search criteria.

**Select (button):** This button will highlight the selected order on the Planning board.

**Report (button):** This button will display a list of all the orders pertaining to the entered search criteria.

**Clear all settings (button):** This button will clear all the search criteria fields. Running Find after clearing all these settings will then display all orders.

The Find dialog has a number of tabs to allow different types of find factors. Each of these is described below:

#### General

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find › General*

Enter or select find options as below. You can select any number of values to use to filter your plan. However if you define too many factors you may eliminate all of your orders!

> **Note:** Items marked with \* above can accept wild card entries as well as selecting a value from the incremental search list.

**Order \*:** Select an order or orders to find.

**Order set:** Select an order set to find.

**Product \*:** Select a product or products to find.

**Product type \*:** Select a product type or product types to find.

**Customer \*:** Select a customer or customers to find.

**Plan group \*:** Select a plan group or plan groups to find.

**Material status\*:** Select a material status to find.

**Material required:** Select a material name to find.

**In bill of material:** Select the material to find all Orders that have it in their Bill of Materials.

**Transport method:** Select a transport method to find.

**Stage:** Select this to find Order in the selected Stage.

**Clear all find lists (button):** - [Icon: Reset Value] Clear all find lists.

This button will clear all the search criteria in the above settings.

**Flow name:** Find all orders with the imputed flow name.

**Row name:** Find all orders with the imputed row name.

**Operation work content:** Find all orders with work content in the selected operation.

**Order description:** Find all orders with the imputed order description.

**Product description:** Find all orders with the imputed product description.

**Timetable\*:** Find all orders with the imputed timetable.

##### Order status

**Confirmed/Provisional/Speculative/Transit:** Include or exclude orders with the shown order status.

**Confirmed/Suggested:** Include or exclude orders with the shown order APS status.

**Not reserve/Firm reserve/Tentative:** Include or exclude orders with the shown order APS/MPS status.

##### Collaborative status

**None/Sent/Planned/Rejected:** Include or exclude orders with the shown order collaboration status.

**Show all sections:** In a cascaded system with multiple sections the planner can enable the option to filter and show all sections. If this is not enabled then only orders in the currently selected section will be shown.

**Show "Find" summary:** When this option is selected the found strip(s) will have their schedule displayed at the top of the High Level planning board. This will only work if the option "Enable drop down style of planning board" in enabled.

**Include made strips:** With this option enabled FastReact will also search the made strips if they are visible on the planning board.

**Extended order status:** Find all orders with the selected extended order status.

**Clear all find lists (button):** - [Icon: Reset Value] Clear all find lists.

This button will clear all the search criteria in the above settings.

##### Other options

**Find locked orders:** This will filter the planning board sop that only orders that have been locked in place will be visible.

> **Note:** This option will only be available if you have a licence to run APS.

**Find manually entered orders:** This will allow the Planner to find orders that have been flagged as "Retain on import". The option will only be visible if you have the import flag "Delete missing orders" set.

**Include all substitute linked orders:** This will allow the Planner to find substitute orders that are linked to orders that have been found using the normal search criteria.

**Find orders where production has started:** This will allow the Planner to only find orders that has production started.

**Find orders where production has not started:** This will allow the Planner to only find orders that has no production started.

**Find orders with parallel processes:** This will allow the Planner to only find orders that have a parallel operation.

##### Show orders starting between

This allows the planner to filter orders to show only those that start (beginning of the strip) between the dates shown.

- [Icon: Reset Value] Clear previously imputed search criteria.

These buttons will reset the dates on the individual date field to their respective default dates.

##### Show orders with delivery dates between

This allows the planner to filter orders to show only those which have delivery dates between the dates shown.

- [Icon: Reset Value] Clear previously imputed search criteria.

These buttons will reset the dates on the individual date field to their respective default dates.

#### Advanced

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find › Advanced*

User Defined Fields can also be used to filter both orders and products.

##### Order user defined fields

This is a list of all the defined UDFs for orders. These UDFs will have been defined during the set up of the FastReact system.

**Field:** The list of predefined UDFs.

**Value:** The value that are being filtered.

##### Product user defined fields

This is a list of all the defined UDFs for products. These UDFs will have been defined during the set up of the FastReact system.

**Field:** The list of predefined UDFs.

**Value:** The values that are being filtered.

##### Customer user defined fields

This is a list of all the defined UDFs for customers. These UDFs will have been defined during the set up of the FastReact system.

**Field:** The list of predefined UDFs.

**Value:** The values that are being filtered.

##### Find by vendor date

**From date:** The start date of the search.

**To date:** The end date of the search.

#### Problems

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find › Problems*

The options in this tab allow further refinement in order to find those orders which have problems.

##### Find problem orders

**Pre-production problems:** Checking this option will find all orders which have Critical Path issues.

**Materials problems:** Checking this option will find all orders which have Material issues.

**Late delivery problems:** Checking this option will find all orders with transport issues.

**Work in Progress problems:** Checking this option will find all orders with WiP issues.

**Flow problems:** Checking this option will find all orders with Flow issues.

One or more of the above options can be selected at a time.

**Orders with any of the above problems:** This will display orders that have any of the above problems, excluding only those that are satisfactory in all ways

**Orders with all of the above problems:** This option will provide a much more rigid filter and eliminate many more orders from the display. It will only display the orders which match all of the above problems.

##### Critical path problems

**Late events:** Checking this option will find all orders which have late events.

**Overlapping events:** Checking this option will find all orders which have overlapping events.

#### Order items

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find › Order items*

This tab will only be visible if the Order Items option in the Licence File has been enabled by Fast React Systems Ltd.

**Customer:** Select the required customer from the drop down list. Once selected the planner can find all order items for that customer.

**Customer reference:** Enter the required customer reference. Once entered the planner can find all order items which have that customer reference.

**Customer style:** Enter the required customer style. Once entered the planner can find all order items which have that customer style.

#### Report

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find › Report*

This tab only becomes visible upon clicking on the Report button. It displays the list of orders matching the search criteria.

**Plan:** The Plan(s) that the found order(s) are planned at High Level and/or Low Level. If the order(s) are not planned this field will be empty.

**Section:** The Section(s) that the found order(s) are planned at High Level and/or Low Level. If the order(s) are not planned this field will be empty.

**Group:** The Group(s) that the found order(s) are planned at High Level and/or Low Level. If the order(s) are not planned this field will be empty.

**Row:** The Row(s) that the found order(s) are planned at High Level and/or Low Level. If the order(s) are not planned this field will be empty.

**Start:** The Start date(s) of the found order(s) if the order(s) are planned at High Level and/or Low Level. If the order(s) are not planned this field will be empty.

**Quantity:** The quantity(s) of the found order(s).

**Order:** The Order Reference(s) of the found order(s).

**Product:** The Product Reference(s) of the found order(s).

**Customer:** The Customer Reference(s) of the found order(s).

Clicking on one of the found orders will automatically filter the High Level board to that particular order.

#### Forecasting

*Context: Main Menu > Planning > High Level Planning > Find › Find › Find › Forecasting*

##### Group forecast attributes

This is a list of all the defined Attributes of Forecasts. These Attributes will have been defined during the set up of the FastReact system.

**Attribute:** The list of predefined Attributes.

**Value:** The values that are being filtered.
