# Main Menu - Setup - Production - Optimise Loading Factors

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Production > Optimise Loading Factors
**Index keywords:** Optimise Loading Factors

---

## Optimise Factors

Optimise loading is used as a way to correctly load the planning resources against certain criteria such as width of machine, volume of dye vessel or minimum order size. They can be applied at either the Order or Product level or both.

Values for each criteria must be specified in either the Order or the Product and must also be specified for the planning resource (planning row). Optimise Loading Factors must have numeric values. Each factor is given a rule to follow.

For example, equal to, greater than, lesser than etc.

Visual warnings are given on the planning board where the optimise values between Order/Product and planning row break the specified rules. The visual warning can be switched to prevent loading altogether if required.

For example, in dyeing where a dye vessel has a maximum capacity of 800kg and a minimum of 300kg (for efficiency and quality reasons). Dye vessel parameters can be set the and then for each Order (dye lot) the weight can be specified for the dye lot. FastReact will then compare the values in both the Order and the dye vessel being planned and warn or prevent loading if the specified rules are broken.

There are separate tabs to define Order and Product related factors. The format of these tabs are identical so will only be shown once here

### Define (Order or Product)

**Enter field name:** Enter the name of a new factor or select and existing one from the list. Factor names can be up to 15 characters long.

#### Rules

The Optimise Factor value for the Order/Product is compared to the value of the planned resource. Each Factor is evaluated according to one of the following rules.

**Off (ignored):** FastReact will ignore any values for this optimise item.

**Less than:** FastReact will check that the Order/Product value is less than the resource value.

**Less than or Equal to:** FastReact will check that the Order/Product value is less than or equal to the resource value.

**Equal to:** FastReact will check that the Order/Product value is equal to the resource value.

**Greater than or Equal to:** FastReact will check that the Order/Product value is greater than or equal to the resource value.

**Greater than:** FastReact will check that the Order/Product value is greater than the resource value.

#### Action if fail

**Warning:** This option will display a warning if the above rules are going to be broken.

**Prevent load:** This option will not allow the loading if the above rules are going to be broken.

**External reference:** Optimise Loading Factors can be imported as part of an Order or Product record. To identify which Factor is being imported FastReact requires an each one to have a unique index or reference number. This will allow factors to be renamed whilst maintaining integrity of the import procedures.

**Insert / Update (button):** This button will Insert a new optimise rule or update an existing one.

**Delete (button):** This button will delete the currently selected rule.

### Rename

Renaming of a factor can take place at any time.

**Order related:** This is a list of all the order related rules that have been created within the FastReact system.

**Product related:** This is a list of all the product related rules that have been created within the FastReact system.

**Enter a new name:** Enter a new factor name here. FastReact will validate the new factor and only allow a rename to be made if the new factor reference does not already exist.

**Rename (button):** This button will rename the selected factor.
