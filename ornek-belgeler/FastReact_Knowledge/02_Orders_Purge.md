# Main Menu - Orders - Purge

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Purge
**Index keywords:** Purge

---

## Purge

Purging orders enables the user to delete a number of orders at once. This may need to be done to reduce the order list to a more manageable size, it will also help in the processing speed of information within FastReact.

Warning: - Purging will permanently remove Orders.

> **Note:** The Purge Orders option will be greyed out (disabled) whilst either the High Level or Low Level Planning boards are open. This is to ensure data integrity.

### Purge Orders

**Which orders would you like to delete:** FastReact has a number of ways in which orders can be purged from the system:

**Completed order only:** This option will delete all completed orders from the database. A completed order is one where the progress through the planned operation (in all sections) is equal to, or more than, the total order quantity. It would also include an order that has been marked as complete.

**Orders entered before a fixed date:** This option allows the user to specify a date so that orders that were entered before this date will be deleted. This maybe useful if you have been using FastReact for some time and you want to clean up the database.

**Order where no production since fixed date:** This option allows the user to specify a date so that orders where there have been no updates since this date will be deleted. This maybe useful if the database requires to be cleaned.

**Orders with deliveries before fixed date.:** This option allows the user to specify a date so that orders that have all delivery dates earlier than specified will be deleted. This maybe useful if the database requires to be cleaned.

**SQL Script:** This is a way of purging orders using an SQL script to interact directly with the database. This should only be used if the user is comfortable with SQL and understands the FastReact database.

**Completed orders only:** This check box can be used with any of the above options, apart from SQL Script, to delete that orders that match the particular selected option AND are marked as complete.

#### Date limit

**Define limit date:** This field will only be displayed if you have selected one of the fixed date options above.

**Purge orders (button):** Click here to remove the selected orders. FastReact will give a count of the orders that will be removed and ask for confirmation before actually deleting the orders.
