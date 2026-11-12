# Main Menu - Reports - Additional Help

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports > Additional Help

---

## Additional Help

### Sample report (using the field "Cum. Delivery qty")

| FastReact Evolution APS | | | | | | |
|---|---|---|---|---|---|---|
| 4.901.100.1 | (31/07/08) | | | | | |
| (#) | | | | | | |
| **Order Code** | **Delivery Date** | **Delivery qty** | **Cum. Delivery qty** | **Ex-factory** | **Del. O/S** | **Del. Made** |
| **PWC** | **31/05/08** | **100** | 100 | 120 | **0** | 100 |
| **PWC** | **31/07/08** | **100** | 200 | 120 | **80** | 20 |
| **PWC** | **30/08/08** | **100** | 300 | 120 | **100** | 0 |
| Subtotal for Order Code: PWC | | | | | | |
| - | - | **300** | - | - | **180** | - |

Using order 'PWC', with 3 deliveries, each of 100 and the final operation ('Ex-Factory') has been updated by 120.

The report is a delivery loop report and uses the field 'Cum. Delivery qty'.

The grey fields are not required in the report. They might just make it easier to see what's happening.

### Explanation of the calculation of 'Del. O/S.'

The formula use two new operations - '<' and '>'. These are simply used to mean Min. or Max. of two numbers.

e.g. 10<20 means the minimum of 10 and 20 i.e. 10. Likewise 100>20 means the maximum of 100 and 20 i.e. 100.

The formula is somewhat daunting '0>(([O.DQC]-[O.OPN_PROG~8])<[O.DQ])', but let's build it up step by step:

| | Delivery 1 | Delivery 2 | Delivery 3 |
|---|---|---|---|
| [O.DQC] <br> Cumulative delivery quantity | * <br> 100 | * <br> 200 | * <br> 300 |
| [O.DQC]-[O.OPN_PROG~8] <br> Less operation progress | * <br> -20 | 80 | * <br> 180 |
| ([O.DQC]-[O.OPN_PROG~8])<[O.DQ] <br> Lower of that and the delivery qty. | * <br> =20 | 80 | 100 |
| 0>(([O.DQC]-[O.OPN_PROG~8])<[O.DQ]) <br> Higher of that and 0 (to remove negatives) | 0 | 80 | 100 |
