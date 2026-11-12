# Functionality - Constraints

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Constraints
**Index keywords:** Constraints

---

## Constraints

An extensible list of capacity restrictions / categories that can be defined on a Group and Row with a consumption value set by Product and Size. Similar to Operations these use the order quantity to calculate a load against the Row / Group based on the value defined on the product multiplied by the order schedule on the Group or Row. Unlike operations, constraints can be varied by size and it is therefore the order size quantity that is used as opposed to the total order quantity in loading calculations.

Calculates a constraint load according to the Order schedule by size and the defined usage (analogous to work content) on the Product. Results can be seen against the Group and Row capacities. Unlike work content, constraints are calculated as a batch calculation much like MRP meaning the overhead on system performance, whilst iteratively planning, is low.

Usage may include areas such as specialist machines, last utilisation (footwear), moulding limitations (bra cups), print screens / masks

This Licence option is configured via:

New licence option under "Products" of "Constraints"

Setup -> Materials -> Constraints Setup -> Planning -> Plan Groups (new constraints tab)

Setup -> Planning -> Plan Rows (new constraints tab)

Products -> Add/Amend (new constraints tab)
