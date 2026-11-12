# Main Menu - Orders - Flows

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Flows
**Index keywords:** Flows

---

## Flow Schedule

*Context: Main Menu > Orders > Flows › Flow Schedule*

Through this dialog the user can create new Flows for orders, keep a record of an original Flow to compare with the current revised Flow, and monitor how well production is satisfying the flow schedule.

#### Flows

*Context: Main Menu > Orders > Flows › Flow Schedule › Flows*

**Flow name:** Enter the Flow name to which the orders will be attach to.

**Orders for this flow:** Once a Flow name has been created, an Agreed amount entered and orders added to the particular flow this drop down list will be populated with the associated orders for the flow described in the Flow name field.

**Made:** This field keeps a running total of the amount of product made per Flow.

##### Flow data table

This table contains information about the current planned status of the selected order, the agreed and original Flow and variances to highlight potential problems. Total values are shown at the bottom of certain columns. These are described below.

The table contains the following columns:

**Date:** The week ending date for the Flow values.

**Planned:** This column contains values from two sources.

- A schedule from the planning board strips .
- A schedule of production updates already entered against each order.

In the case of multi-section planning systems only data from the final section will be shown.

These schedules are combined to show a total schedule of goods that will be available, ex factory or ex DC/warehouse. This will include any transport required and a time allowance for any work that needs to be completed at the DC/warehouse. It does NOT include any transport to the customer's final location. Values in the column are shown in Blue.

**<< Cum:** The cumulative planned quantity to that date. Values in this column are shown in Navy.

**Original:** The original flow schedule. This column will be empty until an Original Flow has been saved (See below).

**<< Cum:** The cumulative original flow to that date.

**Agreed:** The Flow that has been agreed with the customer. You have the option of manually entering values into this column or you can use the button marked 'Copy Agreed Flow from Planned' button to automatically fill in these values.

**<< Cum:** The cumulative agreed flow to that date.

**Variance:** This column shows the difference between the Cumulative Planned and the Cumulative Agreed columns. Negative values are shown in red and indicate that the current plan will not satisfy the Flow requirements as set out in the Agreed Flow column.

##### Totals

**Delivery::** This shows the total of all deliveries in the table.

**Planned::** This shows the total of the planned column. If the total planned is less than the total of deliveries this value will be in Red.

**Original::** This shows the total of the Original Flow column.

**Agreed::** This shows the total of the Agreed column. If the Agreed total is less than the Delivery total then the value will be shown in Red. If the total Agreed is more than the Delivery total then the value will be shown in Purple. If the two values are the same then the value will be shown in Green.

**Copy Original Flow from Planned (button):** This button allows the Planned Flow to be copied into the Original Flow column. This will ensure zero variances and would be useful when creating a flow for the first time.

> **Note:** The new values will not be saved until you save them so that this action can be aborted by closing the dialog.

**Copy Original Flow from Agreed (button):** This button allows the Agreed Flow to be copied into the Original Flow column.

**Copy Agreed Flow from Planned (button):** This button allows the Planned Flow to be copied into the Agreed Flow column. This will ensure zero variances and would be useful when creating a flow for the first time.

> **Note:** The new values will not be saved until you save them so that this action can be aborted by closing the dialog.

**Copy Agreed Flow from Original (button):** This button allows the Original Flow to be copied into the Agreed Flow column.

**Save (button):** This button will save the Flows.

**Delete (button):** This button deletes the selected Flow

### Allocate Orders

*Context: Main Menu > Orders > Flows › Flow Schedule › Allocate Orders*

This tab becomes visible when the Flow name has been entered and values have been entered in the Agreed column and then saved. With this tab, orders can be selected from a list to associate with the Flow name.

**Allocate order to this flow:** This is the name of the flow as detailed in the Flows tab.

**Exclude orders:** This will, when check boxes are checked, exclude any orders with that particular status.

**Order list:** This list will contain every order, unless there are any Excluded, as detailed above, that is not associated to a flow. Check boxes are provided against each order so that checked orders will be associated with the flow. To the left of the order list a description with the amount of orders without flows will appear.

**Update (button):** Upon clicking this button all checked orders will be associated with the flow.

### User Defined

*Context: Main Menu > Orders > Flows › Flow Schedule › User Defined*

##### User defined text values

If the FastReact system has any Flow UDFs set up, then this tab will becomes visible when the Flow name has been entered and values have been entered in the Agreed column and then saved.

**Field name:** This is a list of pre-defined, user entered values.

**Value:** These values can be entered in a Flow by Flow basis.

### Rename

*Context: Main Menu > Orders > Flows › Flow Schedule › Rename*

Renaming of a flow can take place at any time.

**Select an flow to rename:** This is a list of existing Orders. Select the Order you want to copy from the incremental search list.

**Enter a new name:** Enter a new order name here. FastReact will validate the new order and only allow a rename to be made if the new order reference does not already exist.

**Rename (button):** This button will rename the selected order.
