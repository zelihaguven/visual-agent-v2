# Main Menu - Tools - Batch Tickets

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Tools > Batch Tickets
**Index keywords:** Batch Tickets

---

## Order Batch Tickets

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets*

This functionality allows FastReact to generate and record a series of unique ID’s, “Ticket ID’s”, against each FastReact Order, Group and Row. Each ticket will represent a finite production quantity (a batch).

### Tickets

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets › Tickets*

This dialog allows the User to produce Batch Tickets for all available strips. The dialog allows the user to define the fields they they wish to see:

[Screenshot: Batch Field selection]

By clicking the [Screenshot: Batch Field selection] button a list of available fields for this dialog are visible and can be enabled (seen) or disabled (hidden).

##### Strips

Each of the headers below can be enabled and disabled using the method explained above.

**Strip ID:** This is the internal FastReact ID for the Strip.

**Order code:** This is the Order reference of the Order as defined in FastReact.

**Product:** This is the Product Reference attached to the above Order.

**Region:** This is the Section that the Strip is currently planned on.

**Product Type:** The Product Type related to the above defined Product.

**Planning Group:** The Planning Group that the strip is currently planned on.

**Planning Row:** The Planning row that the strip is currently planned on.

**Start Date:** The start date of the planned strip.

**End Date:** The end date of the planned strip.

**Strip Quantity:** The quantity on the strip.

> **Note:** This is not the same as the Order Quantity as the Order may have been split in to multiple strips.

**Delivery date:** The Delivery date of the Order or the due in next section date of the Strip, if using multiple sections.

**UDF - for example Sample Ref:** Order UDFs can also be selected and enabled.

##### Ticket Information

**Batch Quantity:** The quantity of the Batch as defined on the Product. This can be manually overwritten on this dialog.

**Tickets:** The number of tickets required based upon the Batch Qty and the Strip Qty.

**Printed Quantity:** This is the Strip quantity that already has had Tickets printed.

**Print?:** A tick to print the Tickets when the Print Ticket button is selected.

##### Date Range

The range over which FastReact will find available Strips to process for tickets. This is setup on the Configure tab.

**Refresh All Data (button):** This button will refresh the displayed data.

#### Selection Information

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets › Tickets › Selection Information*

**Strip Count::** The number of selected strips.

**Operations to be Printed::** The number of Operations to be Printed.

**Tickets per Operation::** The total Tickets per operations.

**Print Tickets (button):** This button will print the Tickets for the selected data.

**View Existing Tickets (button):** This button will display the data for Tickets that have already been displayed.

**Tickets for this Order (button):** This button will create Tickets for the selected Order.

### Ticket From ...

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets › Ticket From ...*

**Order::** This is the Order reference of the Order as defined in FastReact. This has to be manually entered.

**Order code:** The Order reference based upon the Order selected above.

**Product:** The Product reference based upon the Order selected above.

**Product type:** The Product type based upon the Order selected above.

**Strip Start Date:** The Strip start date based upon the Order selected above.

**Strip End Date:** The Strip end date based upon the Order selected above.

**Delivery date:** The Delivery date based upon the Order selected above.

**Region:** The Planning Board where the Order selected is planned.

**Group:** The Plan Group where the Order selected is planned.

**Row:** The Plan Row where the Order selected is planned.

**Quantity:** The Strip quantity of the Order.

**Batch Quantity:** The Batch Quantity based upon the Product Batch or the manually entered Batch Qty on the Ticket. This can be manually overridden here.

**Number of Tickets:** The number of tickets to be Printed based upon the calculated Tickets on the Ticket. This can be manually overridden here.

**Printed Quantity:** This is the number of tickets printed. Batch Quantity x Number of Tickets.

**Print Tickets (button):** This button will print the Tickets for the selected data.

**View Existing Tickets (button):** This button will display the data for Tickets that have already been displayed.

**Tickets for this Order (button):** This button will create Tickets for the selected Order.

### Configure

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets › Configure*

#### Settings

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets › Configure › Settings*

**Date range for included Strips:** This is the Section that the Strip is currently planned on. The range is the week number and the week dates are displayed below.

**Refresh (button):** This button will refresh the week number range.

**Include High Level Strips:** This option allows the user to include High Level strips as well as Low Level strips.

**Print Production Ticket:** This option allows the user to print the Production Ticket.

**Hide strips with zero quantity:** This option will hide any strips that have a zero quantity in the Ticket list.

**Exclude Suggested Orders:** This option will exclude Suggested Orders from the Ticket list.

**Report selection:** This is a drop down list of available Ticker reports that can be printed. Reports are created using the Report Form report creator.

#### Included Planning Sections

*Context: Main Menu > Tools > Batch Tickets › Order Batch Tickets › Configure › Included Planning Sections*

**Operation List:** This is a list of optional Planned operations. At least one of which must be enabled to produce the Tickets.

**Close (button):** This button will close the Batch Ticket dialog.
