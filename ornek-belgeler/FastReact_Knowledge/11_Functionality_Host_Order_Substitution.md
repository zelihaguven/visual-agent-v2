# Functionality - Host Order Substitution

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Host Order Substitution
**Index keywords:** Host Order Substitution

---

## Host Order Substitution.

### How it works.

The idea behind this piece of functionality is to allow the Planner to wholly or partially confirm an Order whilst maintaining the integrity of the plan.

There are a few caveats to this functionality:

- Confirmed Orders cannot be split across boards or Collaborative partners.
- The total quantity for all Confirmed orders cannot exceed the quantity for Provisional order, unless the ability to over substitute is enabled.

Confirmed orders will be placed on the planning board automatically, after substitution. These orders will be placed automatically in the starting point of the original Provisional strip. If the Confirmed quantity is equal to the Provisional strip quantity then the Provisional strip will be removed altogether and only the Confirmed strip will be seen. If the confirmed strip quantity is less than the Provisional strip quantity then the difference will remain as a reduced length Provisional strip planned AFTER the newly created confirmed strip.

### Orders Add/Amend.

The linking point for the Nett Off is set on the Planning tab of the Orders Add/Amend dialog, for instance on the Confirmed Order. This field, Host Order Substitution, will hold the name of the Order which will be Netted Off, for instance a Provisional Order. On the Netted Off order (Provisional Order), the total quantities for ALL associated orders will appear in the Substitute field. (This field may increase as more (Confirmed) orders are associated with the (Provisional) order).

### The Load List.

Using the example above.

On the High Level and Low Level planning boards the Provisional Order(s) will appear as normal orders which can be planned at High Level and then in Low Level. The associated Confirmed Orders will appear highlighted in yellow in the High Level Load List. These Orders do not get planned.

Double clicking on one of these Orders will display the Substitute Order dialog.

### Substitute Order

**New order to be planned:** This is the name of the (Confirmed) Order which will replace the Nett Off order, (Provisional).

**Group:** This is the Group on which the new (Confirmed) Order will be planned. This is defined on the Order Add/Amend dialog in the Plan in Group field.

**Order to be replaced:** This is the name of the Nett Off Order, (Provisional).

**Quantity:** This is the quantity of the new (Confirmed) Order and also the amount which will be Netted Off the Provisional Order.

**Stage:** This is the Stage which relates to the planned operation.

**Balance:** This is the outstanding quantity on the new (Confirmed) Order.

### Strip Data

If the Provisional order has been split each strip will appear here as a separate entry.

**Group:** The Group on which the (Provisional) strip is planned.

**Row:** The Row on which the (Provisional) strip is planned.

**Start date:** This is the start date of the (Provisional) strip.

**Plan qty:** This is the amount on the planned (Provisional) strip.

**Replace qty:** This is where the Planner will enter the Substitution or Nett Off quantity. This amount cannot exceed the Plan qty for each (Provisional) strip.

### The Planning Board.

Once the (Provisional) Order has been Substituted by the new (Confirmed) Order, it will automatically be planned wherever the (Provisional) Order is. This may be at either High Level or if the (Provisional) Order is planned at Low Level, the new (Confirmed) Order will replace the beginning of that (Provisional) strip.
