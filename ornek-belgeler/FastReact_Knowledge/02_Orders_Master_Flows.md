# Main Menu - Orders - Master Flows

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Master Flows
**Index keywords:** Master Flows

---

Master Flows Schedule

Flows are a licensable option and, when switched on, the Flow dialog is enabled. If, however, a more comprehensive Flow schedule is required, the Flow dialog can be upgraded to the Advanced or Master Flow Schedule dialog.

This is done via the Setup - Production - Flows dialog and selecting the option 'Use Master Flow' dialog.

Through this dialog you can create new Flows for orders, keep a record of an original Flow to compare with the current revised Flow, and monitor how well production is satisfying the flow schedule.

## Flows

**Return to today (button):** - [Icon: Return to todays date] Return to todays date.

This button will return the flow dates to 'todays' date.

**Flow name:** Enter the Flow name to which the orders will be attach to.

**Orders for this flow:** This is a drop down list of all the orders associated with the Flow.

### Date scale

This is the date range over which the Flow is planned.

**Subtotal Planned:** This is the planned subtotal.

**Cum Planned:** The cumulative planned quantity to that date.

**Subtotal Flow (original/agreed):** This is the subtotal amount of the original/agreed flow.

**Cumulative Flow (original/agreed):** This is the cumulative amount of the original/agreed flow.

**Difference:** This row shows the difference between the Cum Planned and the Cumulative Original/Agreed rows. Negative values are shown in red and indicate that the current plan will not satisfy the Flow requirements as set out in the Agreed Flow row.

### Flow

This is the name of the Flow. Right click on the Flow name to access:

**Edit:** Edit the Flow name.

**Delete:** Delete the Flow

**Rename:** Rename the Flow

**Include:** These check boxes will allow the user to access the Original and Agreed hyperlinks. Only one check box can be checked at a time.

**Subtotal:** This is the subtotal amount on the flow for the Original Planned and the Agreed Planned amounts.

**Save (button):** This button will save the Flows.

**Create (button):** This button will create new Flows.

### Planned

**Original:** This shows the total of the Original Flow row in the subtotal column. Right clicking on the text produces:

Copy Original Flow from Planned

This hyperlink allows the Planned plan to be copied into the Original Flow column. This will ensure zero variances and would be useful when creating a flow for the first time.

> **Note:** The new values will not be saved until you save them so that this action can be aborted by closing the dialog.

**Copy Original Flow from Agreed (button):** This hyperlink allows the Agreed plan to be copied into the Original Flow column.

**Agreed:** This shows the total of the Agreed row in the subtotal column. Right clicking on the text produces:

**Copy Agreed Flow from Planned:** This hyperlink allows the Planned plan to be copied into the Agreed Flow column. This will ensure zero variances and would be useful when creating a flow for the first time.

> **Note:** The new values will not be saved until you save them so that this action can be aborted by closing the dialog.

**Copy Agreed Flow from Original:** This hyperlink allows the Original plan to be copied into the Agreed Flow column.

**Allocate Orders:** This hyperlink, when clicked, opens the Allocate orders dialog. With this hyperlink, orders can be selected from a list to associate with the Flow name.

**Allocate order to this flow:** This is the name of the flow as detailed in the Flows tab.

**Exclude orders:** This will, when check boxes are checked, exclude any orders with that particular status.

### Order list

This list will contain every order, unless there are any Excluded, as detailed above, that is not associated to a flow. Check boxes are provided against each order so that checked orders will be associated with the flow. To the left of the order list a description with the amount of orders without flows will appear.

**Update (button):** Upon clicking this button all checked orders will be associated with the flow.

**Close (button):** This button will close the Allocate Orders dialog and return to the Master Flow dialog.

### User Defined

This hyperlink, when clicked, opens the User defined text values dialog. With this hyperlink, values can be given to predefined field names. UDFs are defined on the General – User Defined Fields option.

**Field name:** This is the name of the UDF as defined at setup.

**Value:** This is the value given to the UDF.

**Update (button):** Upon clicking this button the UDFs associated with the Flow will be saved and the User defined text values dialog will close and return to the Master Flow dialog.

**Cancel (button):** This button will cancel any changes and close the User defined text values dialog and return to the Master Flow dialog.
