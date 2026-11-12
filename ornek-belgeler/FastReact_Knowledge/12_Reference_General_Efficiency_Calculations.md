# Reference - General - Efficiency Calculations

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > General > Efficiency Calculations
**Index keywords:** Efficiency Calculations

---

## Absolute v Multiplicative

1. Absolute - whereby the production per day (or period) is multiplied by the LOWER of the efficiency values to calculate the actual production.
2. Multiplicative - whereby the production per day (or period) is multiplied by the PRODUCT of the efficiency values to calculate the actual production.

For Example:

In a system where there is a capability to produce 1000 garments per day when operating at 100%, the result of applying the Absolute Efficiency approach or the Multiplicative Efficiency approach is demonstrated below:

| Manufacture Quantity | | | | | | |
|---|---|---|---|---|---|---|
| **e.g. 1000 per day @ 100%** | | 1000 | 1000 | 1000 | 1000 | 1000 |
| **Product Type Efficiency** | | 85% | 85% | 85% | 85% | 85% |
| **Learning Curve Efficiency** | | 75% | 80% | 85% | 90% | 100% |
| **100% Production** | | 1000 | 1000 | 1000 | 1000 | 1000 |
| **Absolute** | | 0.75 | 0.80 | 0.85 | 0.85 | 0.85 |
| **Absolute Production <br> (Lowest efficiency * Qty)** | | **750** | **800** | **850** | **850** | **850** |
| **Multiplicative** | (0.85 x 0.75) | 0.6375 | | | | |
| | (0.85 x 0.80) | | 0.68 | | | |
| | (0.85 x 0.85) | | | 0.7225 | | |
| | (0.85 x 0.90) | | | | 0.765 | |
| | (0.85 x 1.00) | | | | | 0.85 |
| **Multiplicative Production <br> (ALL efficiencies * Qty)** | | **637.5** | **680** | **722.5** | **765** | **850** |
