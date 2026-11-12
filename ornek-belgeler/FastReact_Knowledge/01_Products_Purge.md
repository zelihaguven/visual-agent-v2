# Main Menu - Products - Purge

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Products > Purge
**Index keywords:** Purge

---

## Purge

Purging products enables the user to delete all products that are not being used, i.e. any products that have not been allocated to an order. The user may want to do this to reduce the product list to a more manageable size, it will also help in the processing speed of information.

### Which products would you like to delete

**All products:** This will delete all products that are not attached to orders or are used as parents for inherited products

**Wild card matching:** This will delete all products whose name matches the wild card text that has been entered. Products that are in use will not be removed

**All of product type:** All products of a specific product type can be deleted. Again Products that are in use will not be removed.

**SQL Script:** This is a way of purging products using an SQL script to interact directly with the database. This should only be used if the user is comfortable with SQL and understands the FastReact database.

**Purge Products (button):** Perform the purge function. FastReact will count the number of products that it would remove and ask for confirmation before actually removing the them from the data database.
