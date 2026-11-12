# Main Menu - Setup - General - Product Types

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > General > Product Types
**Index keywords:** Importing Data, Product Types

---

## Product types

All products in FastReact are allocated to a Product Type. These provide default values for newly created products; existing products will not be changed if amendments are made to a Product Type, only new Products will be affected. Additionally, the planning board views can identify different product types in different colours.

FastReact will not be able to create Products unless at least one Product Type has defined.

### Define

**Product type name:** Enter the name of a new Product type or select one from the list.

**Product type list:** This is a list of all the defined Product types.

**Insert / Update (button):** This button will insert a new Product type or update an existing one.

**Delete (button):** This button will delete the selected Product type.

#### General

**Description:** You can enter a 50 character description for each Product type.

**Planning board colour (button):** Each Product type can be given a colour to allow easy grouping of similar Products on the planning board. Click on the panel to open a dialog for colour selection.

**APS planning:** **Priority (0-255):** This option allows the user to define an APS priority to the Product Type. This will then be used by APS to prioritise the planning of that Product Type.

**Collaborative id:** When Collaboration has been enabled on the system, this option will appear. The events that will be collaborated between the Host and the Remote systems will have the same id here.

#### User values

##### User Defined Values

**Field:** This is the name of the UDF, as defined under Setup - User Defined.

**Value:** This is the user typed value for the UDF.

**User value:** This is an arbitrary value field which is used mainly in Costings.

#### Operations

##### Operations work content table

**Operations:** This is a list of pre-defined Operations.

**Work time:** Work time (also referred to as Work Content) is used by FastReact to calculate the load a specific quantity places on the capacity of a resource.

For example, how long will it take to produce.

Enter the default work content by Operation for this Product type. When entering Products, Work Content can be overridden on a Product by Product basis.

**Used:** Place a 'x' against each Operation that is used on this Product type. Operations that have non zero work content will be automatically flagged as Used. Operations not selected will not be listed against any Product associated with this Product Type. This allows for a long list of Operations to be created, perhaps in a vertical company configuration, where only certain selected Operations need to be visible on any single Product type.

#### Events

###### Events table

**Event:** This is a list of all the Events as defined by the Framework.

**Disabled:** Each Event can be disabled at Product type level. This has the effect of filtering through all of the Products which are attached to that particular Product type.

### Rename/Copy

Renaming of a Product Type can take place at any time.

**Select an Product Type to rename:** This is a list of existing Product Types. Select the Product Type that requires renaming from the incremental search list.

**Enter a new name:** Enter a new Product Type name here. FastReact will validate the new Product Type and only allow a rename to be made if the new Product Type reference does not already exist.

**Rename (button):** This button will rename the selected Product Type.

**Copy (button):** This button will copy the select Product Type to the new named one.
