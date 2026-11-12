# Main Menu - Setup - Production - Change Allowances

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Production > Change Allowances
**Index keywords:** Change Allowances

---

## Define Change Allowances

A planning system must allow for the real life efficiency losses that occur when a new product is introduced into production. Typically for machine based processes this takes the form of a Change Allowance also referred to as Change Over.

When a machine changes from one Product to another there may be several alterations and amendments to the machine settings required, even including the replacement of some parts - for example, different warps and wefts on weaving machines. Since the time to make these changes eat up the available capacity of the resource, this time is not available for production and must be taken into account in planning.

For example, 1000 units made up of 10 different products would probably take much longer to produce than 1000 units made up of 2 different products.

##### In FastReact, Change Allowances are used to account for this non-productive time.

A number of Change Allowances can be defined within FastReact. These can then be attached manually to an Order during the planning process or they can be assigned automatically according to which Product type they are changing from and to.

For example, If the weaving plan is changing from a 'plain fabric, black warp' to a 'patterned fabric, red warp' then FastReact can be configured to automatically use a long Change Allowance however if changing from 'plain fabric, black warp' to a 'patterned fabric, black warp' then it could apply a shorter Change Allowance.

The choice of which Change Allowance it will use is decided using a matrix of Product Types.

### Define

A list of changes can be defined in this table. Give each a meaningful name, up to 15 characters long, to help the planner remember which one to use. In the second column in the table, enter the number of minutes for which production will stop when the relevant change allowance is selected.

**Update (button):** This button will update any changes to this dialog

#### Matrix

This tab will only be visible if automatic change allowances are selected.

**Select base product type (change from):** Select from the list the product type from which production is changing.

**Product type list:** Enter into the table the change allowances that are required to be inserted between the base product type and each of the product types listed. When set to automatic change allowances, FastReact will insert the appropriate number of minutes between strips where it can find an entry in this matrix. Where there are no change allowances required there is no need to set up zero values between product types.

**Update (button):** This button will update any changes to this dialog.

### Define

This tab will allow the user to define multiple attributes that affect the change over time..

**Attribute Names:** Up to four attribute names can be defined.

**Change times:** Enter the change over times for the four defined attributes.
