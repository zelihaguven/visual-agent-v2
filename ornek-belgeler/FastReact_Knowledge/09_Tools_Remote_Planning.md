# Main Menu - Tools - Remote Planning

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Tools > Remote Planning
**Index keywords:** Remote Planning

---

## Remote Planning

When licenced this option will allow the Main system to send data packages out to Supplier sites. This will allow the Supplier site to update progress, operations, events etc. and if enabled return the data to the Main site. This allows the Main site to have an overall picture of the planning environment, whilst giving the Supplier sites autonomy.

### Send Package

**Select Package:** Select the Package that will be sent to the Supplier from the pre-defined drop down list.

**Plan Group:** Select the Group, from the dropdown list, that the Supplier belongs to.

**Update (button):** Update the selected Package.

**Delete (button):** Delete the selected Package.

**Send (button):** Send the selected Package.

#### Package Setup

##### Editable events

All the Events in FastReact are available to send to the Supplier/Remote site. These Events are sent upon selection.

##### Editable operations

All the Operations in FastReact are available to send to the Supplier/Remote site. These Operations are sent upon selection.

##### Read only events

All the Events in FastReact are available to send to the Supplier/Remote site. These Events are sent upon selection but the recipient cannot edit them.

##### Read only operations

All the Operations in FastReact are available to send to the Supplier/Remote site. These Operations are sent upon selection but the recipient cannot edit them.

##### User defined values

All the Order and Product UDFs in FastReact are available to send to the Supplier/Remote site. These UDFs are sent upon selection.

##### Optional Headers

Optionally, Product details and Customer details can be sent. These are sent upon selection.

##### Has events due within "x" days

Enter the desired number of days for the Supplier/Remote site. Only Orders that have events due within this figure will be sent.

#### Package email

**Recipient:** Select the email recipient from the drop down list.

**Message:** The sender can type a message here which will appear in the body of the email.

#### Filters

##### Order Status

The sender can select the Order Status for the Orders that will be sent. Only Orders with the selected Status will be sent.

##### Product type

The sender can select the Product Type for the Orders that will be sent. Only Orders with the selected product Type will be sent.

##### User Defined Value

By selecting this option the user can send only Orders that match the selected UDF.

##### Log

This is the Log of the sending process.

### Receive Package

**Retrieve Package (button):** Check the C:\Fast_React\Remotes folder for any packages.

##### Change Orders - Select an Order to review its changes

The user can select individual Orders to import, view or change.

##### Date Changes

**Event/Operation Name:** Based upon the selected order, above, all the Event/Operation changes will be displayed here for that Order.

**Original Target:** The original Target date.

**Revised Target:** The revised Target date,

##### Updated Progress

Based upon the selected Order this field will list out all the Production changes for that Order.

**Operation name:** The name of the operation to be updated.

**Original Quantity:** The original quantity on the schedule.

**New Quantity:** The new quantity on the schedule.

##### Log

This is a log of what is happening while the Package is being Imported.

**Import Selected Orders (button):** Import the selected Orders. By default all Orders are selected on the Package but the User has the ability to de-select Order. These de-selected Orders will not be imported in to FastReact.
