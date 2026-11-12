# Main Menu - Setup - Materials - Material Data

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Materials > Material Data
**Index keywords:** Material Data

---

## Material Setup

*Context: Main Menu > Setup > Materials > Material Data › Material Setup*

To be able use FastReact’s material functionality the user must first enter the material specifications. These Specifications can be associated with each Product or Order along with a utilisation to build up a required demand of materials based on the current production plan.

### Define

*Context: Main Menu > Setup > Materials > Material Data › Material Setup › Define*

**Material name:** Enter the name of a new material or select an existing one from the list.

**Description:** Enter the material description that relates to the unique material name.

**Material group:** Select a material group from the incremental search list. If the user does not want to assign a group to a material or there are no defined groups, this can be left blank. The group is used as a means of sorting materials in reports and also for linking materials required for orders to event target dates for those orders. See also Main menu - Setup - Materials - Groups

**Materials consumed in section:** Each material must be consumed at some point in the production process. Specify here at which stage in the process this occurs. Specifying <First in section> will force FastReact to ignore the Operation setting below and link the material to the first valid operation on each individual product.

**Consume at operation:** This allows further refinement of the consumption point.

For example, threads may be consumed at the sewing operation but fabric would be consumed earlier than this, at cutting. See also <First in section> above.

**Release at operation:** This allows further refinement of the release point.

#### Options

*Context: Main Menu > Setup > Materials > Material Data › Material Setup › Define › Options*

**Non Phased availability:** By selecting this option FastReact will calculate the quantity of this material needed but accumulate the entire quantity for the first day of the schedule. If this option is not enabled then FastReact will spread the material schedule out over the lifetime of the order.

**Ignore lead time on category mask:** Categories can be defined on a Product or Order BOM

For example, Warp or Weft yarn.

The category must be predefined as a material in FastReact, and each material can have a purchase lead time. With this option enabled FastReact will ignore any lead time defined on the category item and use the material lead time of the main BOM item when carrying out material calculations.

**Hide on critical path:** If this option is enabled then FastReact can display materials within the critical path events list for each order. This allows the user to see whether particular materials have passed key progress points. This functionality can be turned off for specific materials.

For example the user may not want to see this information for materials that are either easy to obtain or are common to a wide range of orders.

**Ignore in MRP calculations:** The materials details with this option checked will be ignored in all MRP calculations.

**Non critical material:** By default all materials are set to a status of critical, however a material can also be defined as non critical. By enabling this option FastReact will still calculate the position of the material but colour the strips on the planning board with Red, Yellow or Green hashes to denote an issue with a non critical material.

**Ignore status:** This option is used in conjunction with the above Non critical material. With this option enabled non critical materials will not be used in MRP calculations.

**Reusable material:** This option tells FastReact that the material is reusable.

**Integer usage:** This option tells FastReact that the material usage will be a whole number.

**Size specific material:** This material is size specific.

**Soft Constraint for APS:** This is used for APS only.

**Purchase and create SWO for this material:** This is used for APS only.

**Do not calculate confirmed orders:** This option will ignore confirmed orders in APS calculations.

#### Other values

*Context: Main Menu > Setup > Materials > Material Data › Material Setup › Define › Other values*

**Leadtime:** Enter into this field the time (in days) it takes for the supplier to actually manufacture the material item after an order has been placed with them. FastReact will then use this information to calculate when the material items should be ordered, if they require purchasing.

**Call off leadtime:** Enter into this field the amount of time (in days) that the supplier requires to deliver materials to the factory once they have been called off. This is used in reporting and allows the production units to give the supplier a call off report each week based on the lead time set in this field.

**Cost:** This is the cost of the material.

**Smoothing offset:** This is the offset, for this material, when Smoothing is applied.

#### User defined values

*Context: Main Menu > Setup > Materials > Material Data › Material Setup › Define › User defined values*

The user may want to add some additional information relating to a Material that does not have a standard field. FastReact has the ability to define additional fields. These fields can be given a value on a Material by Material basis. These can then be used for reporting purposes. User data fields must first be defined elsewhere.

**Update (button):** This button updates the material in the database.

**Delete (button):** This button deletes the current material.

### Rename

*Context: Main Menu > Setup > Materials > Material Data › Material Setup › Rename*

Renaming of an order can take place at any time.

**Select a material to rename:** This is a list of existing Materials. Select the Materials that requires renaming from the incremental search list.

**Enter a new name:** Enter a new Materials name here. FastReact will validate the new order and only allow a rename to be made if the new Materials reference does not already exist.

**Rename (button):** This button will rename the selected Materials.
