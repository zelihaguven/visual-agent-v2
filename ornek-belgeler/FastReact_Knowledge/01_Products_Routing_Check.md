# Main Menu - Products - Routing Check

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Products > Routing Check
**Index keywords:** Routing Check

---

## Routing Check

This dialog allows the User to mass check the Products to ensure that they have a Routing applied to them

### Manage products linked to orders that have no valid routing defined

**Select customer:** Select the customer to check.

> **Note:** We would advise a consistent naming convention for products as this will make future operation much easier. We strongly recommend that spaces are not used as part of the product name and, as such FastReact will strip from the beginning and end of the product name any spaces found.

**Refresh list (button):** - [Icon: Old refresh] Refresh list.

This button refreshes the list of products with incomplete or invalid routings.

**Include partially defined routing (button):** Enabling this option will include incomplete routings as well as missing routings.

### No routing defined

This will be the list of all the Products which have an incomplete or missing routing.

### Check for invalid Routings after conversion

This will find any routing where there is a parallel stage in slots 1, 2 or 3. Routings are sorted by the latest Order delivery date for any order using the Product so as not to overlook Products with later deliveries.

Orders that are marked as complete are ignored by default.

**Include complete orders (button):** This option will include complete order as well as uncompleted orders.

**Customer (button):** This drop down list will allow the Planner to run a check against a selected Customer.

#### Count

This is the number of returned Products that have an invalid Product routing.

**Run check (button):** This button will start the check to find all the Products with an invalid routing.
