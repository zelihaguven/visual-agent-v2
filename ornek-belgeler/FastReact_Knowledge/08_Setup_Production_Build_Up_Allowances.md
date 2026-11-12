# Main Menu - Setup - Production - Build Up Allowances

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Production > Build Up Allowances
**Index keywords:** Build Up Allowances

---

## Build Up Curves

A planning system must allow for the real life efficiency losses that occur when a new product is introduced into production. Typically for operator based processes this takes the form of a Build Up Allowance also referred to as an Operator Learning Curve.

When a new product is introduced, the output efficiency improves day by day as operators become familiar with the product and any new manufacturing technique or skills. Different operators learn at different rates and complex designs take longer to learn than simple designs

A number of Build Allowances can be defined within FastReact. These can then be attached manually to an order during the planning process or they can be assigned automatically according to which Product type they are changing from and to.

For example, if the production is changing from a 'shirt' to a 'jacket' then FastReact could automatically use a complex learning curve but if changing from 'shirt' to another 'shirt' then it could omit a Build Up Allowance, or insert a simple allowance.

FastReact makes the choice of which Build Up Allowance to use using a matrix of Product Types.

> **Note:** The efficiency value taken from the Build Up Allowance is considered in conjunction with other efficiency settings within FastReact such as Efficiency Profiles and an efficiency value associated with each order. These values can be evaluated in 'absolute' terms (apply the lowest) or multiplied together.

### Define

**Build up name:** Enter the name of a new Build Up Allowance or select an existing one from the list. Names can be up to 15 characters long

**Days:** This table show the number of days in each of the definable periods. The size of a definable period can be from 1 or more. The size of a period is defined elsewhere.

**% (in this period):** Enter the expected efficiency for each period to create the shape of the Build Up Allowance. As a value is typed, the shape of the curve is shown in the graph at the right hand side, allowing mistakes to be easily spotted.

#### Build up percentage

This graph will show a representation of the build up curve.

**Continue build up form previous strip.:** When ticked (it is ticked by default), this will allow the continuation of the build up curve from the previous strip.

**Clear previous updates (button):** This button will allow the planner to re-start a learning curve on an order that has already had production updates applied to it.

**Insert / Update (button):** This button will insert a new Build up curve or update an existing one.

**Delete (button):** This button will delete the selected curve.

### Rename

Renaming of a Build Up Curve can take place at any time.

**Select an curve to rename:** This is a list of existing curves. Select the curve that requires renaming from the incremental search list.

**Enter a new name:** Enter a new curve name here. FastReact will validate the new curve and only allow a rename to be made if the new curve reference does not already exist.

**Rename (button):** This button will rename the selected curve.

### Matrix

This page will only be visible if automatic build insertion is enabled.

**Select base product type (change from):** Select from the list the product type from which production is changing.

**Change to:** This table will give a list of all product types that have been created. The list is populated by dragging build up allowances from the list on the right into the Build Name column. FastReact will then automatically insert this build up allowance when it detects a change from the base product type (above) to the product type in the change to column.

**Insert / Update (button):** This button will insert a new matrix or update an existing matrix.
