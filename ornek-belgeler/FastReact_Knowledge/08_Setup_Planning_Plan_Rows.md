# Main Menu - Setup - Planning - Plan Rows

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Planning > Plan Rows

---

## Planning Board Rows

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows*

An important function of FastReact is as a capacity planning and Order scheduling tool. Plan Rows, often referred to as Lines, are the real planning resources on which you will plan your orders. Each Row represents the resource that will do the work of the planned operation(s) converting raw materials on the way to becoming finished goods. Each Row requires a capacity per hour and a working calendar which FastReact uses to calculate how long each order will take to produce.

Some typical examples of the operations represented by planning Rows for different industries are shown below:

- Apparel Manufacture - Rows are Sewing Lines of several operators.
- Dyeing and Finishing Industry - Rows are Dye vessels
- Weaving Industry - Rows are Looms.
- Apparel Sourcing - Rows are factories (owned or subcontract)

### Define

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Define*

**Select group to view:** Select a group from the list or enter '\*' to show all groups. This is used to limit the content of the list below to only those rows that belong to the selected group.

**Row name (unique):** Enter the name of a new row or select an existing row from the list. Row names can be up to 30 characters long.

**Insert / Update (button):** This button will either insert a new row or update an existing one.

**Delete (button):** This button will delete the selected row.

#### Properties

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Define › Properties*

**Group to which this row belongs:** Select the Group to which this row will belong.

**Factory name:** This is an additional field (which we have arbitrarily called 'Factory') that can be used to link Rows. You may type freely into the text box but any previously defined 'Factories' are available in the drop down list. Factory names may be up to 15 characters long. This field has no functional purpose in FastReact but can be used for reporting purposes.

For example, report all Rows in factory 'ABC'.

**Row property:** You can enter any text here up to 30 characters long Any previously defined properties will be selectable from the list to help with data constancy, where many rows may need the same properties.

Each Product can be given a list of properties that will be matched to this Row property. If a Row property does not match one of the Product properties then it will not be possible to load any Orders for that Product on the Row.

Row Properties should be used to identify a particular feature of the Rows to which they are attached.

For example, A blouse may be made quite happily on a Blouse line but not on a Skirt line. Properties called 'BLOUSE' a another called 'SKIRT' could be created and attached to the appropriate lines. The user will be able to load any product whose property value matches 'BLOUSE' on this line but not on the ‘SKIRT’ line.

**Copy from row:** In many cases the row name itself is used as the Property. To speed up the initial set-up operation you can click the 'Copy from row' check box rather than type the row name.

**Route:** Select the normal (default) Route that Products use when being produced on the selected Row. This will ensure the appropriate product work content will be used and materials.

**Transport method:** Select the normal (default) Method that Orders use when being produced on the selected Row.

**Row link property:** This field works in a similar way to the Row Properties field and users can either enter free text or select from the Drop Down list.

**Calendar to use:** Select the Calendar to use for the selected Row. The Row capacity (per hour) will be multiplied by the daily working hours in this Calendar to give a capacity per day for planning.

**Available capacity:** Enter the capacity for the Row per attended hour. FastReact requires capacities to be defined per hour as this capacity will be multiplied by hours worked per day taken from a Row calendar. Units of capacity must be the same as those used for the work content of a Product. There is no hard and fast rule on units and they may vary according to both the industry and the level of detail at which you want to plan, or limited by the information available .

The table below shows several examples:

| Capacity Units | Work Content Units | Resultant Output |
|---|---|---|
| Minutes per Hour | Mins per unit | Units per hour |
| Units per Hour | Units per Unit (always 1) | Units per hour |
| Picks per hour | Picks per metre | Metres per hour |

**Capacity factor:** This is a multiplying factor that can be used to amend the actual capacity of a Row on a daily basis. This factor is used in one of two different ways depending whether the Row belongs to a group in which capacity can be varied by strip.

**Normal (Fixed) Capacity Rows:** For normal, also called fixed capacity Rows, the capacity factor is a percentage factor and is set to 100% by default.

For example, the capacity of the Row will be 100% of that defined under the Available capacity. The user can set this factor to other default values and this will be used to calculate the available capacity of the Row. This factor can be altered for selected days on the planning board itself e.g. 125% represents 2 hours planned overtime on an 8 hour shift.

**Variable Capacity Rows:** For rows in a variable capacity group, this factor can be altered on a strip by strip basis. This set-up is used in environments where the capacity of a planning resource is not fixed, but changes according to the Product being manufactured.

e.g. if producing this style then the Line has 20 operators, if producing that style then the line has 24 operators. Often this is a function of the style (line balancing).

In this type of set-up the Capacity Factor is simply a default value that is applied when a new Order is loaded. In this case the Capacity Factor is not a percentage figure but an absolute figure.

For example, a capacity of 60 minutes per hour multiplied by a capacity factor of 8 would give a resultant capacity of 480 minutes per hour not 4.8 (60 x 8 / 100) minutes per hour.

**Throughput time:** Enter the number of days that it takes the first unit feeding into the planned Operation to the first unit coming off the planned Operation. This option is used to determine the Feed on Date for both production schedule reporting and critical path target dates.

> **Note:** Throughput time should not to be confused with capacity. Throughput is a function of the Row set-up and the method of manufacturing and is independent of the number of units produced and the work content per unit.

**Customer profile:** This is a drop down list of all the defined Customer Profiles.

**Efficiency profile:** Select the Profile from the list that applies to the selected Row.

##### Options

**Holding row:** Typically a Holding Row is used as a divider between Rows in different Groups or factories or as a temporary location to place new Orders when they are being re-planned. Strips placed on holding rows will be ignored in calculations as if they were still in the load list. Holding rows will be marked as yellow on the planning board.

**Subtotal row:** This is used in conjunction with rows on variable capacity planning groups. When enabled this row will not be available for planning but will subtotal the capacity factors of all preceding planning rows, to the top of the planning board or to a previous subtotal row. The subtotal row will display the subtotal values along with the difference between the subtotal row's own capacity factor. Typically a subtotal row is created at the end of a logical grouping of rows and has a capacity factor equal to the total of that row grouping. When real planning rows are loaded, the subtotal row will show the total load on those rows along with the variance between this load and the capacity of the subtotal row.

**Section count and Section width:** In some businesses a planned resource may run at a specific speed but, because of its configuration, it can make more than one of the Product at once. If the resource had, three sections it could make at three times the speed of another resource, running at the same speed but with only one section.

In addition to the above some planning resources.

For example, narrow fabric looms, may be able to make multiple products within each section depending on the width of the section and the width of the product. So a three-section loom with each section 100mm wide, will be able to make 9 widths of 30mm fabric or 6 widths of 45mm fabric. The production rate will therefore be very different depending on the fabric width being woven.

**Row external id:** This is the external ID for the selected Row. This ID is used in the importing of the Update import file.

**Minimum batch and Maximum batch:** When the batching function is enabled in FastReact you will be able to enter into these fields the minimum and maximum batch sizes that this machine can handle. FastReact will then use these figures when calculating how many batches are required when an order is planned on this machine.

#### Order values

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Define › Order values*

When enabled, the user will be able to assign optimise values to the Planning Rows.

##### Optimise loading values

**Factor:** This is the previously defines value. See here.

**Value:** The value can be entered an a Row by Row basis.

#### Product values

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Define › Product values*

When enabled, the user will be able to assign optimise values to the Planning Rows.

##### Optimise loading values

**Factor:** This is the previously defines value. See here.

**Value:** The value can be entered an a Row by Row basis.

### Constraints

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Constraints*

**Select a row to update:** This is the name of the row that the constraints will be applied to.

##### Constraint / Capacity matrix

This is a list of Constraints and there corresponding capacity values for the selected row.

**Update (button):** This button will Update the selected Planning row with the constraint.

### Copy

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Copy*

This option can be used to create new rows by copying an existing row.

> **Note:** Rows can also be created from within the Low Level planning board.

**Select a row to copy:** This is a list of all the rows that have been created within the FastReact system.

**Enter a new name:** Once the row that has to be copied has been selected, the new row name can be entered here.

**Copy (button):** This button will copy the group.

### Rename

*Context: Main Menu > Setup > Planning > Plan Rows › Planning Board Rows › Rename*

Renaming of a Row can take place at any time.

**Select an order to rename:** This is a list of existing Rows. Select the Row that requires renaming from the incremental search list.

**Enter a new name:** Enter a new Row name here. FastReact will validate the new Row and only allow a rename to be made if the new Row reference does not already exist.

**Rename (button):** This button will rename the selected Row.
