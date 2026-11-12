# Main Menu - Orders - Transfer

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Transfer
**Index keywords:** Transfer

---

## Order Transfer

This option allows the user to transfer order quantities from one order to another existing or new order.

> **Note:** Transferring from an order that has already been started is not allowed.

### Transfer

**Select source order:** Select an order from the incremental search list.

#### Original order table

The table below the list will show you all of the deliveries that are defined on the selected order.

**Date:** This is the user entered delivery date, obtained from the Orders Add/Amend dialog.

**Quantity:** This is the user entered delivery quantity, obtained from the Orders Add/Amend dialog.

**Select or create destination order:** Either an existing order or a new typed order can be selected. In the latter case the new order will have all of the properties of the source order. Confirmation will be required before FastReact will create the new order.

#### Destination table

The table below the destination list will show all of the deliveries that are defined on the destination order.

**Date:** This is the user entered delivery date. This can either be from the Orders Add/Amend dialog or, in the case of a new Order, manually typed in here.

**Quantity:** This is the total quantity for that order. This can either be from the Orders Add/Amend dialog or, in the case of a new Order, manually typed in here.

**Add quantity:** This is the amount which will be transferred from the original order quantity on the Original order table to the destination order on the Destination table.

If the delivery dates on the destination order match exactly those of the source order the quantities will be transferred exactly as you specify in this table. If, however, they are different then FastReact will do the best job that it can in moving delivery quantities to the dates in the destination order.

FastReact will check for the following error conditions:

- The transferred quantity cannot be zero;
- You cannot transfer more than the source order quantity;
- You cannot make changes that would reduce the destination order quantity.

A Total quantity for each delivery on the destination order can be entered or an incremental change value in the Add quantity column can be entered.

> **Note:** Transferring the total quantity from the source order to the destination order results in the deletion of the source order.

**Transfer (button):** This button initiates the required transfer.
