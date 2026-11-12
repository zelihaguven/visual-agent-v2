# Functionality - Extension Dates

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Extension Dates
**Index keywords:** Functionality, Extension Dates

---

## Extended Delivery Date

Clients can hold an “extension date” against an Order record, this allows the client to “Extend” the Delivery Date without interfering with the Critical Path etc.

On the Orders Add/Amend dialog there is a new check box next to the Delivery Date:

[Screenshot: Extension date]

This check box allows the Planner to enter an extended date and relevant reason note:

[Screenshot: Extension strip]

This extended date will be reflected on the High Level and Low Level planning boards in the form of a red dot on the planned strip. This red dot tells the Planner that the strip is planned late based upon the extended date:

The Extension comment is available on the Text Display on the HL and LL Planning Boards and the following reporting fields are also available for this feature:

- Order::Delivery date (inc. extensions) \*\*
- Order::Days late (inc. extensions)
- Order::Delivery extension date \*\*
- Order::Delivery extension note \*\*
- Strip::Delivery date (inc. extensions)
- Strip::Days late for delivery (inc. extensions)
- Strip::Delivery extension date
- Strip::Delivery extension note
