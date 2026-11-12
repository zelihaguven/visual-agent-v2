# Main Menu - Setup - Production - Efficiency Profiles

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Production > Efficiency Profiles
**Index keywords:** Efficiency Profiles

---

## Efficiency Profiles

In most real environments, different planning resources have different efficiencies, e.g. operators have different skill levels, some machines run faster than others. This efficiency can depend on the type of product being produced.

For example, some operators may be good at jackets but not shirts while others are good at shirts or blouses but not jackets.

Each individual planning resource can have a different efficiency for each different type of product. These differences are allowed for, in FastReact, by using Efficiency Profiles.

Efficiency Profiles allow the planner to define an efficiency value for each of the Product Types that have been defined. Each of the planning resources can then be given one of the defined Profiles. Several resources may share the same Profile or there can be a new Profile for each resource.

> **Note:** The efficiency value taken from the Efficiency Profile is considered in conjunction with other efficiency settings within FastReact such as Build Up Allowances and so on. These values can be evaluated in absolute terms (apply the lowest) or multiplied together.

This mechanism is at the heart of APS and plays a key role in determining where the orders may be placed to the best effect.

This dialog has separate tabs to create efficiency profiles and another to define their properties.

### Define

The planner must create efficiency profiles before their properties can be set. Efficiency profile names can be up to 15 characters long. The planner can also delete profiles here, but they will not be able to delete a profile if it is still attached to a planning group or row.

**Efficiency profile name:** New profiles are entered here and are visible in the list bellow.

**Insert (button):** This button will insert a new profile.

**Delete (button):** This button will delete the current selected profile.

### Product types

**Select efficiency profile:** Select, from the drop down list the profile which will be associated with the product types.

**Product type table:** Select an efficiency profile from the list. When a profile is created it is initialised so that all product types have an efficiency value of zero. In other words, any group or row with this profile attached will not be able to make any product types at all. Not very useful.

A list all of the product types that have been created is visible in the table. Against each one of these, an efficiency value between 0 and 255 can be entered to indicate the production efficiency of specific product types when planned on groups with this profile.

**Update (button):** This button will update the selected efficiency.

**Copy down (button):** This button is used to copy a value from the currently selected table row to the next row. This is a quick way to enter the saved value against a number of product types.

#### Rename

Renaming of a profile can take place at any time.

**Select a profile to rename:** This is a list of existing profiles. Select the profile that requires renaming from the incremental search list.

**Enter a new name:** Enter a new profile name here. FastReact will validate the new profile and only allow a rename to be made if the new profile reference does not already exist.

**Rename (button):** This button will rename the selected profile.
