# Functionality - Consolidated Order Progress

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Consolidated Order Progress
**Index keywords:** Consolidated Order Progress

---

## Consolidated Order Progress

There is an option available from Order Add/Amend dialog - Order Status. Right click on a strip in Low Level and High Level boards to Consolidate by any Order, Product, Prod type or Customer text UDF (not numbers). The consolidate UDF is global and not by user. Only supervisor status can change the value. This is setup in the dialog on a Configure tab.

The resultant Grid shows only those operations not hidden in the normal Status charts. The grid can show different products and as such it is not possible to filter out operations that are not valid on a product but these show 'n/a' instead of a number. Also operations are sorted across the page in the default sequence but the user

can change this sequence and it is remembered. The operation columns can be hidden, by user, to allow different users to concentrate on some operations and not others. Totals for Delivery quantity and Progress quantity are shown at the bottom.

[Screenshot: Consolidate dialog]

On the configure tab the user can set what criteria the Order Progress will be consolidated against. A product UDF or an Order UDF can be selected or, if these are not required, Consolidation can be done against the Order Base Code.

[Screenshot: Consolidate dialog]
