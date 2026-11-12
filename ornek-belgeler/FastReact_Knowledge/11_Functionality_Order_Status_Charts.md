# Functionality - Order Status Charts

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Order Status Charts
**Index keywords:** Order Status Charts

---

## Order Status Charts.

This chart allows you to easily visualise the progress of an order through all operations that are required on the relevant product. The chart can be accessed from the Order Add/Amend dialog, or from the Strip menu on the Low Level and High Level planning boards.

The chart has the following components.

### Left hand side

The left hand scale shows a list of valid operations with the earliest in the production route at the bottom and the latest one at the top.

### Right hand side

The right hand scale shows the date when each operation was last updated, and the group (if known) where the operation was carried out. This can only be determined for planned operations, as unplanned ones are not updated by group, only in total.

### Bottom axis

This scale has its right hand limit as the order quantity.

### Progress bars

The progress for each operation is shown by means of a coloured bar extending to the right. The bar may have a number of different subdivisions to show the different status of progress. There is a legend across the bottom of the chart as a reminder.

### Colour coding

**Progress (Made):** Any production updates will be shown as a Green section, with the actual value shown in a green label.

**Waiting:** This represents the work in progress waiting at this operation and this is shown in Blue. So if the preceding operation has made 300 and there has been 100 passed though this operation the bar will show a green section representing the 100 made with a blue section representing the 200 waiting for this operation. The waiting quantity will be shown in blue label.

**Total:** This Yellow section fills out the bar between the made/waiting sections and the full order quantity.

**Mark complete:** If an operation/section has been flagged as complete the made part of the bar will be shown in Purple. This is to indicate that no matter how much has been made there will be no more progress on the order.

**WIP invalid?:** The work in progress for an operation should always be zero or more. Negative work in progress suggests that less work has passed through preceding operations than has been made at the current operation. This is practically impossible, however it could happen if data entry is not up to date, or entries have been missed. FastReact will warn of this problem by turning the bar red.

**Overdue:** FastReact can calculate how much of an order should have progressed though each pre-planning board feeder operation if the planned schedule is to be met. It knows the quantities per day demanded by the planned operation(s) and when this schedule will start. It also knows how much time is required ahead of this schedule for each operation. If it finds that you have not progressed sufficiently through the feeder operations it will show this with a black arrow across the top of the operation bar. A black label will show the shortfall quantity.
