# Functionality - Planning Methodologies - Embellishment Planning

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Planning Methodologies > Embellishment Planning
**Index keywords:** Embellishment Planning

---

## Embellishment Planning

Embellishment planning is accessed from the High Level board via either a right click on the selected strip or via the F5 button when a strip is selected and shows the numeric schedule for the selected strip(s). This numeric schedule can be manually manipulated by the planners. It also allows the planners to view Prior and Next operations, Parallel Routings etc. depending on how the system has been configured.

FastReact embellishment planning is designed to automatically schedule planned strips for stages preceding the primary planned stage. In apparel, this will be SEW. Typically, this will be used to create planned strips for embellishment strips such as embroidery, print and for cutting. The sewing schedule will drive the preceding schedules with overriding rules governing the minimum quantity per day.

For example: whilst sewing maybe scheduled as 10, 20, 30, 50, due to operator learning curves, the cutting schedule would automatically be planned as 50, 0, 60

[Screenshot: Embellishment Plan]

**Stage:** This is the stage (operation) that the planner wants to plan. In a multi-section plan there will be multiple Rows, one for each Stage (operation).

**Group:** This is the group to which the stage is planned on.

**Made:** This is the quantity for the Stage (operation) that has already been made.

**Planned:** This is the planned quantity for the Stage (operation).

**Manual:** This flag indicates that the Stage (operation) has a manual schedule against it.

### Numeric schedule

**Stage:** This is the Stage to which the numeric schedule will apply, as defined in the Stage to Plan.

**Group:** This is the selected group in which the planned operation will be planned.

**Planned:** This is the planned quantity.

**Made:** This is the made quantity.

**Schedule:** The planner enters the required production amounts here.

### Stage (cumulative quantity)

**Save (button):** This button will save the planning changes.

**Undo (button):** This button will undo the changes.
