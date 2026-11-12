# Main Menu - Setup - Production - Customer Profiles

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Production > Customer Profiles
**Index keywords:** Customer Profiles

---

## Customer Profiles

With customer accreditation more strictly being followed, manufacturers need to control allocation of orders to factories better.

Current property matching on an order may not be enough to cater to this requirement due the multiple relationships between customers and factories.

For Example, Group 1 could allow Customer1 and Customer2 while another Group, (Group 2), could allow Customer1 and Customer3 to be made. If a Customer1 order is received it could be allowed on either of the Groups but Customer2 would only be allowed on Group1 and Customer3 would only be allowed on Group2.

This requires the option, "Enable group/customer profiles", under Setup - Configure - Planning - Configure to be enabled.

Reporting fields "Customer match (group)" & "Customer match (row)" are available to the "Strips" and "Strip Plan by Day" reporting loops under the "Strip" field group.

> **Note:** These fields will return 0 (no match), 1 (match) or "n/a" (not planned at this level) if the strip's order's customer is not valid for the customer profile defined on the planned group/row (irrespective of the value of the "override customer profile" of the order).

> **Note:** Automated functions such as APS or Embellishment Planning will not recognise a customer group profile in their routines but strips will be subsequently off-loaded if the customer group is not valid for that customer on that group / row.

### Define

**Customer profile name:** This is where the Customer Profile name is enabled.

**Insert / Update (button):** This button will insert a new Customer Profile name.

**Delete (button):** This button will delete the selected Customer Profile name.

### Customers

**Select Customer profile:** This is where the user will select Customer Profile name that they want to configure.

#### Customer matrix

**Customer:** This will be a list of all the Customers defined in the system.

**Enabled:** This check box will enable the selected Customer as valid against the selected Customer Profile.

**Update (button):** This button will update the Customer Profile.

**Copy down (button):** This button will copy the enabled selection down the list.

### Rename

Renaming of a Customer Profile can take place at any time.

**Select a Customer Profile to rename:** This is a list of existing Customer Profiles.

**Enter a new name:** Enter a new Customer Profile name here. FastReact will validate the new Profile name and only allow a rename to be made if the new Profile reference does not already exist.

**Rename (button):** This button will rename the selected Customer Profile.
