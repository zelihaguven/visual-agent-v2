# Main Menu - Tools - Remote FOB / CIF

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Tools > Remote FOB / CIF
**Index keywords:** CIF, Remote FOB

---

## FOB/CIF Package

When licenced this option will allow the Main system to send data packages out to Supplier sites. This will allow the Supplier site to update progress, operations, events etc. and if enabled return the data to the Main site. This allows the Main site to have an overall picture of the planning environment, whilst giving the Supplier sites autonomy.

### Send Package

**Select Package:** Select the Package that will be sent to the Supplier from the pre-defined drop down list.

**Plan Group:** Select the Group, from the dropdown list, that the Supplier belongs to.

**Update (button):** Update the selected Package.

**Delete (button):** Delete the selected Package.

**Send (button):** Send the selected Package.

#### Package Setup

##### Events to include

All the Events in FastReact are available to send to the Supplier/Remote site. These Events are sent upon selection.

##### Operation to include

All the Operations in FastReact are available to send to the Supplier/Remote site. These Operations are sent upon selection.

##### User defined values

All the Order and Product UDFs in FastReact are available to send to the Supplier/Remote site. These UDFs are sent upon selection.

##### Editable user defined values

The Order UDFs can be changed by the Supplier/Remote site. Allowing this is by selection.

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

**Fetch Package (button):** Check the C:\Fast_React\Remotes folder for any packages.

##### Change Orders - Select an Order to review its changes

The user can select individual Orders to import, view or change.

##### Date Changes

**Event/Operation Name:** Based upon the selected order, above, all the Event/Operation changes will be displayed here for that Order.

**Original Target:** The original Target date.

**Revised Target:** The revised Target date,

##### Updated Schedule

Based upon the selected Order this field will list out all the Production changes for that Order.

**Date:** The date of the change to the schedule.

**Quantity Planned:** The planned quantity on the schedule.

**Quantity Shipped:** The shipped quantity on the schedule.

##### User Defined Fields

If the Supplier/Remote site has been given permission to change the UDFs then this is where the changes, by Order, can be seen.

**User Defined Field Name:** The Name of the UDF which has been changed on the selected Order.

**Original Value:** The Original value of the UDF.

**Revised Value:** The new value of the UDF.

##### Log

This is a log of what is happening while the Package is being Imported.

**Import Selected Orders (button):** Import the selected Orders. By default all Orders are selected on the Package but the User has the ability to de-select Order. These de-selected Orders will not be imported in to FastReact.
