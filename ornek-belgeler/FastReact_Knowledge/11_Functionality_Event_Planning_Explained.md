# Functionality - Event Planning Explained

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Event Planning Explained
**Index keywords:** Event Planning Explained

---

## Event Planning.

### Critical Path Event Management for Flow Line Production (Phased Production)

#### Explanation of Reference Points

All events must be related (in terms of negative or positive offset days) to one of the following reference dates.

[Icon: Func Events Explained]

The options above with the prefix \*\* give you the option to link to different sections.

For example, the planner maybe planning two sections 'CUT', 'SEW' and may have a QC check at 'CUT' so the planner can link this event to section 'CUT'.

> **Note:** If you are planning two boards 'CUT' and 'SEW' and a cross over occurs, i.e. the orders from section 'CUT' are arriving to late for the planning section 'SEW' Fast React will highlight this problem for you to rectify.

 'CUT', 'SEW' and 'FINISH' which could all be linked.

[Icon: Func Strips Explained]

| 1 & 2 | The delay and transport time to get raw materials from the supplier to the manufacturing sight. The delay till next ship and transport time can be set globally, by region. |
|---|---|
| 3 | The largest negative offset for the pre-online operations (Load Centres). These offsets can be set globally, by product type, by individual product or by individual strip. |
| 4 | The throughput time (i.e. time taken for one item from feeding on to feeding off the planned operations). This is defined for each row on the planning board. |
| 5 | The largest positive offset for off-line finishing operations (Load Centres). These offsets can be set globally, by product type, by individual product or by individual strip. |
| 6 & 7 | The delay and transport time to get finished goods from the manufacturing sight to the distribution warehouse. The delay till next ship and transport time can be set globally, by region or by group. |
| 8 | This is the time needed by the despatching warehouse to prepare finished goods for despatch after they have arrived from the manufacturing site. This can be set globally, by region or by group. |
| 9 | The delay time until completed garments in the section can be placed on the relevant transport. |
| 10 | The transport time for the completed garment to reach the destination point. |
