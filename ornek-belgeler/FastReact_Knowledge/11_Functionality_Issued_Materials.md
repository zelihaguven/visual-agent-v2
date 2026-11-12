# Functionality - Issued Materials

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Issued Materials
**Index keywords:** Issued Materials

---

## Issued Materials

This module is used to calculate the outstanding material balance on each Order from a total material required minus any issued quantity.

This method allows the passing of the total quantity per material for each PO to FastReact. FastReact will then dynamically pro-rata the issued quantity, from the clients ERP system, for example, by PO based upon the planned date and the matching PO reference. FastReact will then calculate the outstanding balance per material per order as TOTAL REQUIRED - ISSUED. This outstanding balance will be compared to the availability of the material to determine if there is any shortfall on the Order.

The TOTAL, the ISSUED and the OUTSTANDING balance by material by planned Order can be viewed on the “Material details” screen accessed via the right click menu on a strip.

Example of Materials details:

[Icon: Func Issue Materials Calc]

### Strip Colour.

On the strip, in materials rotation, when the material calculation has been run then the strip will have the worst case of all the materials. In the above Query screen the resultant strip will be RED since there are materials with Shortfalls.

Notice the new Material Issue colour. Blue is now used to donate the Issues Materials. This same colour will also be seen on the strip on the planning boards.

| Blue | Materials Issued quantity. |
|---|---|
| **Green** | Material stock quantity. |
| **Red** | Material shortfall. |

The length of the “issued” portion represents the quantity of the Order that may be produced given the amount of material issued to date. The colours on the strip will always represent the worse case material (i.e. the material with the least issued quantity and earliest shortfall date), these may be different for the same material on any one Order. The calculation will be by Order, not by individual strip.
