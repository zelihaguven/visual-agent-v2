# Main Menu - Setup - Planning - Plan Groups

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Planning > Plan Groups
**Index keywords:** Planning Groups

---

## Planning Groups

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups*

Within each Section the user must define at least one Group. A Group may represent a factory, a set of machines or any other logical grouping of capacity items. For High Level planning, the capacities of the Groups are the planning resources. In addition Group capacity (defined by Operation) is used in the Loading Bar Charts for both High Level and Low Level plans.

Typically planning rows at Low Level are assigned into logical planning groups e.g. same factory or subdivision within a factory.

Groups must be attached to a Planning Board before they will appear as a planning resource or be considered by APS as a capacity. Groups which are defined as being part of a Distribution Centre (DC) are exempt from this rule.

### Define

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Define*

**Plan group name:** Enter the name of a new group or select one from the list. Groups will be sorted alphabetically so it is important to name each group carefully to ensure it is placed the sequence you want them to appear. The easiest way to do this is to start each group with a number. It is good practice to leave a gap of 10 between each group to allow insertions at a later date if necessary.

**Insert / Delete (button):** This button will insert a new Planning Board or update an existing Planning Board.

**Delete (button):** This button will delete the currently selected Planning Board.

#### Properties

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Define › Properties*

**Planning board:** Allocate each group to an existing Planning Board, unless the group is only to be used as a distribution centre.

Groups must be attached to a Planning Board before they will appear as a planning resource.

**Planning section:** Allocate each group to an existing section. This defines where this group (and it’s capacity) will appear as a planning resource. Groups not attached to a planning board may be left unattached to a section.

**Group property:** Enter a group property or select one from the list. There is a limit of 30 characters for group properties. Group properties are used to match products to groups, either to warn of potential mismatch or event to prevent loading. The property is also used in selection of suitable groups within APS.

**Consolidate property:** The high level planning board can consolidate your planning groups by a number of different properties, all of which are defined against each group. This entry allows the user to add another property specifically for consolidation. This value is not used by any other FastReact function although it is available for reporting.

**Efficiency profile:** Select an efficiency profile from the list. This is used, like group properties, to identify groups that are suitable to make certain product types and the efficiency of that product type on this group.

**Target efficiency:** This option, enabled via the Setup - Configure - High Level dialog, allows a target efficiency to be entered against a group. This efficiency will be reflected on the High Level planning board in the form of bar chart markers.

**Calendar name:** Select a calendar to be used in the calculation of capacity for this group. See also Group Operations.

**High level display divisor:** This will divide the capacity by the entered value for the selected Group.

**Group location:** Select a location from the list appropriate to this group. This location (along with a specified transport method and calendar) will determine the time of transport for goods being delivered to or returning from this Group.

> **Note:** If a valid transport Route is not defined to or from this location then the default transport method and time will be used.

**Materials Location:** Select the location for materials warehouse. This is used in Materials Planning and APS.

**Transport method:** Select the normal transport method for returning goods from this Group.

**Use product route:** Select the Route that Products use when passing through Operations in this Group. This will have an impact on the work content and also the materials usage for the product within this group.

**Suppliers:** Select the Supplier which will be associated with the selected Group. Normally this functionality will be used by Purchase Order processing.

**Throughput time:** Enter the number of days that it takes the first unit going onto a planning resource to the first unit coming off that resource. This option is used to determine the Feed on Date for both production schedule reporting and critical path target dates. This Group default can be over-ridden on a planning Row by Row basis for Low Level planning.

**Minimum and maximum batch size on this group:** The minimum and maximum batch sizes that are applied to this group when using batch planning.

**Owner:** This is a free form entry field to store any data you want. This field is available in the report generator.

**Customer profile:** This is a drop down list of all the defined Customer Profiles.

**Cut off time warning:** This option is tied in with shifts on the calendar. When a time is entered, a ‘marker’ will be placed on the planning board at the entered time.

**Confirmed warning days:** The number of days anything planned on this group will receive a warning for.

**Group external ID:** The external ID of the Group. This is used in importing instead of the Group name.

**Collaborative id:** When Collaboration has been enabled on the system, this option will appear. The planning group that will be collaborated between the Host and the Remote systems will have the same id here.

##### Options

**This group can be a distribution centre:** Only groups selected here will be listed as possible distribution centres when defining Customer details.

**This group operates with batches:** This will apply the batching methodology to the selected Group

**Prevent batches splitting across non working days:** Used in conjunction with the above, this option will force the batch to only plan on working days.

**Allow capacity to be varied by individual strip:** Enable this option if 'Variable' capacity planning is required.

In brief, variable capacity means that the capacity of the resources vary according to the Product that is being produced or even according to the availability of labour. In this scenario the planning resources do not have a fixed hourly capacity but one that can vary for each planned Order.

**Hide capacity factor display:** The capacity factor, which is used to adjust capacity of low level planning board rows on a daily basis, may be hidden if this functionality is not required. This will simplify the appearance of the display.

**Multiplicative efficiency calculations:** FastReact can calculate efficiencies one of two ways. These are termed 'Multiplicative' or 'Absolute'. An explanation can be found here.

**Hide this group in the loading barcharts:** When enabled the selected group will not be displayed in the loading barchart dialog.

For example, this maybe useful if there is a group setup as a DC and to have this group in the loading charts may confuse people as it has no capacity or loading.

**Hide this group on the High Level plan:** When enabled the selected group will not be displayed on the high level planning board.

For example, this maybe useful if there is a group setup as a DC and to have this group displayed on the high level planning board may confuse people as it has no capacity or loading.

**Hide this group in the Low Level load lists:** When enabled, anything planned on the selected group at High Level will not be seen in the Low Level load lists.

**Infinite capacity for APS:** This only used for use with FastReact APS.

**Ignore group for APS:** This only used for use with FastReact APS.

**No materials requirement for in this group:** Orders that are planned in this group will have no materials requirement.

**This group is for despatch only:** Only groups selected here will have the ability to use the despatch planning function.

**Remote site controls capacity:** This collaborative option allows the Remote site to control, via importing, the capacity of this Group..

**Collaborated consolidated Group capacity (defaults to Row capacity):** Group capacity and total Row capacity for all the Rows within a Group are independent values. This option will use the Group capacity from the Remote site instead of the total consolidated Row capacity.

#### User value

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Define › User value*

UDFs can be configured at the Plan Group level.

##### User defined text values

This is a list of the UDFs defined at the Plan Group level along with their corresponding values.

##### Forecast attributes

This is a list of the Forecast attributes defined at the Plan Group level along with their corresponding values.

#### Remotes

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Define › Remotes*

If you have Remote Access Services enabled and you have defined certain users as FR Remote (RAS) recipients then this tab will be visible.

The purpose of this option is to allow you to restrict the data that is sent to each RAS user. If you define a user here then that user will automatically only receive data that is related to the selected group. This will include production planning information and also target dates for Production events.

If you specify '(disabled)' , the default option, then this restriction is turned off and the normal RAS package definitions will apply.

##### User name for Remotes

This is a list of the users which have right to use FR Remote (Remote Access Services). This is enabled on the Users input dialog.

**Send production details:** This check option will always send production details with the remote package.

**Send event details:** This check option will always send event details with the remote package.

### Operations

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Operations*

**Select a group to update:** Select a group from the drop down list.

**Planning section:** This is the section relating to the group selected from the above list.

**Planning board:** This is the planning board relating to the group selected above.

##### Options

**Operation name:** This table contains a list of all operations that have defined. Operations marked as 'Planned' in the Operation configuration are be identified. Information can be edited for those operations that belong to the section to which the selected group is assigned. Other operations will be shown, but grayed out.

**Capacity:** Enter the capacity per working hour. FastReact will use the calendar attached to the Group or, where defined attached to each Operation, to calculate the capacity for each working day.

**Prep(aration) and Standing time:** These two fields are only valid for unplanned operations. Preparation time takes place before the operation whilst Standing takes place after the operation has been completed.

For unplanned operations FastReact assumes that your goods will need to progress through each operation at a rate equal to that determined by the strips on the planning board.

For example, in apparel, sewing is planned to produce 1000 pieces per day and therefore both cutting and embroidery must also produces 1000 pieces per day to avoid running out of work for sewing, or building of too much work in progress. However these operations are carried out a known number days earlier than sewing That is; embroidery has a 3 day throughput and cutting a 2 day throughput. Goods which need to be both cut and embroidered must start in cutting 5 days before starting in sewing but only 2 days before if they do not need to be embroidered.

FastReact will ignore the preparation time for the first operation in the process for any product.

Preparation time is fixed for each group and cannot be amended for individual orders however standing time can be amended for each order.

**Enable:** This field needs to be checked in order to tell FastReact that the operation configuration is used in the selected group.

###### Override values for each operation

If the system has the Licence Option 'Advanced Event Setup' turned on, then the items below will be added to the Options table. If the Licence option is not turned on the options below will be hidden.

**Calendar:** Select the working Calendar used to calculate the capacity of the Operation within the selected Group. The default calendar is the calendar which was selected when defining the group properties above.

**Group:** Operations may share capacity between groups.

For example, a single machine which is used at two different points in the production process. To allow work content to be entered properly the user would need to create two different operations. This would also allow FastReact to calculate the dates when work would hit the machine at the two different points in the process.

This option allows the user to tell FastReact to use the capacity of this operation from another group; the capacity of the operation in the selected group being ignored.

**Operation:** Operations may share capacity. This option allows the user to tell FastReact to use the capacity of another operation in the same group or another operation in the 'Cap. from group' the capacity of the operation in the selected group being ignored.

**Mat(erial) Location:** The user can define a different material warehouse location here, this is useful when the operation is carried out at a different factory, so the material warehouse for Cutting maybe in Factory 1 but the material warehouse for sewing is in Factory 2. FastReact will then use this information when performing material calculations to determine where the Raw materials are required.

### Constraints

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Constraints*

**Select a group to update:** This is the name of the group that the constraints will be applied to.

##### Constraint / Capacity matrix

This is a list of Constraints and there corresponding capacity values for the selected group.

**Update (button):** This button will Update the selected Planning Group with the constraint.

### Rename

*Context: Main Menu > Setup > Planning > Plan Groups › Planning Groups › Rename*

Renaming of a Planning Group can take place at any time.

**Select an order to rename:** This is a list of existing Planning Groups. Select the Planning Group that requires renaming from the incremental search list.

**Enter a new name:** Enter a new Planning Group name here. FastReact will validate the new Planning Group and only allow a rename to be made if the new Planning Group reference does not already exist.

**Rename (button):** This button will rename the selected Planning Group.
