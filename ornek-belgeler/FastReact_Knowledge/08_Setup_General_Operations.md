# Main Menu - Setup - General - Operations

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > General > Operations

---

## Operations

*Context: Main Menu > Setup > General > Operations › Operations*

Operations define the stages of the process from raw materials to finished goods. Operations take place sequentially in the defined list although individual Products may skip particular operations.

To be able to use FastReact, one Operation, at least, must be created. For the configuration to be valid, at least one Operation must be marked as 'Planned', although there can be several planned Operations in the list. FastReact uses the work content from planned operations to calculate the load on the capacity resources

For example. In apparel manufacture the typical list of Operations might include:

- Cut
- Embroider/Print
- Sew
- Finish
- Pack

'Sew' will normally be the 'planned' Operation of this list as it represents the key resource within the business. It is possible to plan several Operations individually.

For example the user could create a plan for 'Cut' and a plan for 'Sew'. This is termed as Cascaded Planning in FastReact. An alternative option would be to use Operation Stages.

Unplanned Operations are typically potential bottleneck areas that service the key planned Operation. In general work should flow through these Operations at a higher rate (excess capacity) than the planned Operation and therefore it is only necessary to monitor loading on these areas rather than actually plan them.

### Define

*Context: Main Menu > Setup > General > Operations › Operations › Define*

**Enter operation name:** Enter the name of a new operation or select an existing one from the list. Operation names can be up to 30 characters long. Operations will be sorted alphabetically so it is important to name each operation carefully to ensure it is placed the correct sequence for your process. The easiest way to do this is to start each operation with a number. It is good practice to leave a gap of 10 between each operation to allow insertions at a later date if necessary.

**Section name:** Select a section to which this operation will belong. Every operation must by linked to a section

**Work content units:** Enter the units that you will use for product work content.

For example Standard minutes, or Standard hours, picks per metre, even just pieces.

This is used as a label throughout FastReact to help and ensure consistency in data entry and interpretation across the business. It does not actually affect any of the functionality within FastReact.

It is essential that the units used for work content for each Operation are the same as used for the Capacity of those operations The following table lists some of the typical examples of work content and capacity used.

| Work Content Units | Capacity | Resulting Output |
|---|---|---|
| Standard Minutes (SMV) per piece | Minutes per Hour | Pieces per hour |
| Pieces per piece (work content is always 1) | Pieces per hour | Pieces per hour |
| Picks per metre | Picks per hour | Metres per hour |
| Stitches per piece | Stitches per hour | Pieces per hour |

> **Note:** Each Operation may have different work content units if required.

For example, in apparel Sewing normally uses SMV’s or SAH but Packing uses simply pieces.

**Display divisor:** FastReact requires all operations to be defined in the same units (e.g. minutes). You may want to enter the work content for some operations in different units.

For example, the work content for some operations may be entered in minutes whilst others in hours. Set a display divisor to 60 for the latter operation then you can enter 60 for operations in minutes and 1 for operations in hours. In either case FastReact will store the data as 60 for both operations to that its internal calculations are consistent.

**Change minutes:** Enter the default fixed time (minutes) required when changing between orders. This change time consumes part of the available capacity for that operation and thus ensures accuracy in the bar charts.

**Uplift percent:** This option is designed to uplift the schedule of the preceding non-planned operation(s) so that they are producing more than the planned operation schedule requires.

For example, a schedule which requires 100 units per day but has an uplift of 5% on the Cutting operation will create a Cutting schedule of 105 units per day. As opposed to the normal 100 units per day.

> **Note:** The uplift will only work for the total order amount.

For example, The order is for 500 units and the cutting operation has a 5% uplift, the schedule will call for 105 units on day one, 105 units on day two, 105 units on day three, 105 units on day 4 but only 80 on day five.

#### Options

*Context: Main Menu > Setup > General > Operations › Operations › Define › Options*

**Create a planned strip for this operation:** This option will create a planned strip for the selected operation. This is used in conjunction with Advanced Routings.

**Drive strip schedule from Order input schedule:** This option will force the selected operation to derive its schedule from the imported or manually typed in Order Input Schedule. This option will only be visible when Advanced Routings has been licenced.

**Use work content in strip length calculations:** This is also commonly referred to as a 'planned' operation. Mark the operations that are to be planned in each section.

For example, this would normally be sewing in apparel, dyeing in a dye house, knitting in a fabric producer or cutting in a cutting room.

These are the operations that FastReact will actually plan. Planned operations represent the key part of the production process. It is the work content of these operations that are used to consume the capacity of the planning resources.

**Add to planned work content for linked operation:** When this option is selected, the selected operation will have its work content added to the linked planned operation.

**Allow capacity multiplier for this operation:** When this option is selected, the operation will factor in the capacity multiplier in its calculations. This will affect the strip length and the what can be produced per day.

**Allow parallel processing for this planned operation:** When this option is enabled, this signifies that the operation can be run at the same time as another operation as defined in the Routes dialog.

**Ignore strip quantity in loading calculations:** FastReact uses the Order quantity and Planned operation work content to calculate the length of time an order will take on the planning row. Some process will take the same time whether you have 1 item or 50 items going through the planned operation.

For example, with special machines count, such as twin needle or bar-tacking machines.

If this option is selected then FastReact will just take into account the work content of the planned operation when calculating the strip lengths.

For example, Sewing time is 4 hours, regardless of machine count.

**Ignore HL strips altogether in Loading calculations:** This option will not use any High Level strips when calculating the loading on the plan.

**Use maximum values in loading calculations (default adds load):** This is used when monitoring machine loading, normal FastReact will add up all the loading values for a given period, however when monitoring the load on specialist machines we only need to consider the maximum number of machines in a period.

**Standing time only - not production operation:** This Operation simply represents a waiting period between two other operations.

For example, dyed or washed items may need to stand to relax for a day before the finishing process can take place. In these cases there are no capacities or work content as such but the standing time still needs to be taken into account when planning the overall process.

Operations that are checked as 'Standing time only' will simply add a specified number of days to the flow of work between adjacent operations. These operations will not appear when defining or amending a Product as they are a function of the process. The actual standing time for these operations is therefore only defined at Group level.

**This operation operates with batches:** This option allow the designated operation to work with batches and alters the calculations accordingly.

**Update batch operation in batch units:** Used in conjunction with the option above, this option will allow the user to update the operation in the batch unit.

**Ignore operation in loading barcharts:** Check this box if there is no need for the selected operation to be visible in the Loading bar charts. Bar charts are used to monitor the load on potential bottleneck operations. If the operation is never a bottleneck (or is a planned operation) select this option to omit this operation from the bar charts.

**Ignore operation in order status charts:** If this option is selected then this operation will not be shown in the Order status charts.

**Ignore operation in Operation progress screen:** If this option is selected then this operation will not be shown in the Update operation progress screen.

**Ignore move days for order status Confirmed:** These are the change times between Orders.

**Ignore move days for order status Provisional:** These are the change times between Orders.

**Ignore move days for order status Speculative:** These are the change times between Orders.

**Ignore move days for order status Transit:** These are the change times between Orders.

**Monitor Work in Progress:** Enable this option to monitor Work in Progress (WiP) for the operation. FastReact defines WiP for any operation as the difference between the quantity produced in that operation and the quantity produced in the previous operation that is also marked as a WiP point. FastReact will draw a red border around any strips on the planning board that have a WiP problem.

**Ignore Work in Progress on strip display:** If only this operation is causing a WiP problem then FastReact will not highlight strips with a 'red border' warning on the planning board. This allows certain operations to be ignored in this function. The standard WiP calculation however is still performed for reporting purposes.

**Progress operation:** Operations can be defined so that they can be used as a progress point. Such operations would not have work content and hence play no part in loading calculations, but would allow progress quantity information to be entered. This function may be used to define check points at various positions through the process route, rather than monitoring every operation.

**Non phased operation schedule:** Normally FastReact will generate operation schedules in line with the schedules for the strips to which the operation belongs. Such operation schedules take account of any throughput times required and working calendars. The operation schedule in this case is phased over the life of the strips on the planning board for that order. However there may be times when the operation must be completed before work can start on subsequent operations as in some batch processes.

For example, a cutting operation feeding sewing where the cut needs to be totally complete before sewing can start. Set the cutting operation to non phased to achieve this.

**Do not allow overlap with next planned operation:** In a multi-planned operation system this option will prevent preceding or subsequent operations from being planned at the same time.

**Use in ticket printing:** This operation will be used in batch Ticketing.

**Allow working in different units:** This option allows the operation to be calculated in different work content units from the other operations in the system.

For example, all planned and non-planned operations in a system might be calculated in Pieces however the Finishing operation might require calculating and reporting in KGs.

With this option enabled a new column called Factor will appear on the Product Add/Amend work content dialog.

**Operation carried out at distribution centre:** Certain operations may occur in a Distribution Centre prior to final dispatch to the customer.

For example, Quality Control checks, repacking or picking.

Enabling this option shows the specified operation taking place in the DC. This will ensure that the appropriate time allowance is included when calculating availability dates.

**Finite capacity for APS secondary constraints:** When enabled the secondary constraints will have a finite capacity.

**Update progress by size:** When enabled this will allow the update of production on the selected operations by size.

**Retain production update details:** When selected FastReact will store daily production update figures for planned and/or unplanned operations.

Replicate this operation

This option will duplicate the operation.

**Delegate work content control to collaborative planner:** When Collaboration is enabled, and the operation will be one of the collaborated operations, the user can assign responsibility for the work content for that operation to the collaborative partner.

**Delegate progress updates to the collaborative planner:** When Collaboration is enabled, and the operation will be one of the collaborated operations, the user can assign responsibility for the update progress for that operation to the collaborative partner.

**Include rejected for operation in order status charts:** This option will include rejected quantities on the Order Status chart.

**Review loading in projection planning:** This option will allow the planner to review the loading on the plan.

**External reference:** This is used for indexing when importing data into FastReact. Enter a unique number to associate with this Operation. This will also need to be used in the import file.

**Short name:** This is a short name for the operation which could be used in report filtering.

**Collaboration id:** When Collaboration has been enabled on the system, this option will appear. The operations that will be collaborated between the Host and the Remote systems will have the same id here.

**Operation stage:** This is the stage at which the selected operation will happen.

**WiP - Too much percentage:** This field allows the planner to define a percentage value at which WiP would become an issue. This will be displayed on the planning board.

**Linked to planned operation:** This will link the selected operation to a nominated planned operation. This will be used when there are multiple planned operations.

**Insert / Update (button):** Insert a new operation or update an existing operation.

**Delete (button):** Delete the selected operation.

### Descriptors

*Context: Main Menu > Setup > General > Operations › Operations › Descriptors*

This functionality allows the User to add a description to an Operation. This means that there can be many operations of the same or similar names but they can be easily identified via their Descriptors.

##### Define descriptors

This is a list of defined descriptors.

**Name:** Enter a new descriptor name here.

**Description:** Enter the new descriptor description here.

**Add (button):** This button will Add the new Descriptor name.

**Rename (button):** This button will Rename the selected Descriptor with the name in the Descriptor field.

**Delete (button):** This button will Add the selected Descriptor.

##### Link descriptors

**Operations:** This is a list of the operation in the FastReact system.

**Descriptors:** This is a list of the descriptors in the FastReact system.

- [Icon: Select All] Select all.

**Select all (button):** This button will select all orders

- [Icon: Invert Select] Invert selection.

**Invert selection (button):** This button selections that are made will be de-selected, others will be selected.

- [Icon: Select None] Clear selection.

**Clear selection (button):** This button will deselect all orders.

**Update (button):** This button will update the links.

### Rename

*Context: Main Menu > Setup > General > Operations › Operations › Rename*

Descriptors allow for the the same operation to have many different descriptions and in turn allows the same operation, with different descriptions, to be part of the production process.

**Select an order to rename:** This is a list of existing operations. Select the operation you want to copy from the incremental search list.

**Enter a new name:** Enter a new operation name here. FastReact will validate the new operation and only allow a rename to be made if the new operation reference does not already exist.

**Rename (button):** This button will rename the selected operation.

### Report

*Context: Main Menu > Setup > General > Operations › Operations › Report*

A detailed list of all the operations and their settings can be viewed on this dialog.

**Print (button):** This button will print the operation list.

### Import options

*Context: Main Menu > Setup > General > Operations › Operations › Import options*

Using the Import options on this dialog allows the user to import production updates for planned operations in different formats.

> **Note:** This option requires Normalised Importing to be enabled.

**Select planned operation:** This is a list of existing planned operations. Select the required planned operation which will have its import settings altered.

#### Import option

*Context: Main Menu > Setup > General > Operations › Operations › Import options › Import option*

**Use default settings in the import configuration dialog:** This is the default setting and as such will use the setting as defined on the Import setup dialog.

**Cumulative production updates by Order:** Regardless of what is defined on the setup import dialog, the selected operation which has this option selected will import production updates cumulatively by Order.

**Cumulative production updates by Group:** Regardless of what is defined on the setup import dialog, the selected operation which has this option selected will import production updates cumulatively by Group.

**Cumulative production updates by Row:** Regardless of what is defined on the setup import dialog, the selected operation which has this option selected will import production updates cumulatively by row.

**Save (button):** This button will save the operation settings on this dialog.

### Synchronised Planning

*Context: Main Menu > Setup > General > Operations › Operations › Synchronised Planning*

Operation stages are the stages through which the operations, defined under the define tab, pass in order to produce a finished article. This form of defining the operation pathway is called Complex Routing.

**Select the Primary stage:** This is a list of all the stages defined in FastReact. At present the list can hold 30 stages. These stages do not need to be in sequence on this list.

Double clicking on one of the stages will assign it as the default operation stage for new orders. This default stage is the Low Level planned operation.

**Synchronise these stages to the Primary stage:** In a multi-stage system, other stages (planned operations) can be synchronised with the default stage (planned operation).

**Update (button):** This button will update the synchronisation.
