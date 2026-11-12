# Functionality - Low Level APS

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Low Level APS
**Index keywords:** APS, Low Level

---

## Low Level APS.

*Context: Functionality > Low Level APS › Low Level APS.*

Low Level APS is a rule based automated planning method that can plan many orders at a time. This is a licence file option so will need to be enabled in order to use the functionality.

#### How it works

*Context: Functionality > Low Level APS › Low Level APS. › How it works*

##### Setup, Descriptions and Configuration:

##### Setup

Once Licenced the Automated Planning System (LL) will be available on the SETUP – PLANNING – PLANNING BOARD OPTIONS dialog under the Licenced Section. Since Automated Planning System (LL) is licenced at a Section Level each section that requires an Automated Planning System (LL) must have this enabled against it. The Totals will also display the Total licenced sections and the Total licenced sections with Automated Planning System (LL) and the number of Sections unallocated and the number Automated Planning System (LL) unallocated:

[Screenshot: LL APS]

In the below example the China planning board has one Section called *Sew*:

[Screenshot: LL APS]

As can be seen in the above screenshot each licenced Sew section has an Automated Planning System (LL). These options are enabled on this dialog per Section and Board.

> **Caveats:** There must only be one planned operation in the system.

The number of Licenced Automated Planning Systems (LL) cannot be greater than the number of Licenced Planned Sections.

##### Descriptions

Once the Automated Planning System (LL) has been setup it can then be configured.

Restart FastReact and open the Low-Level Planning Board. There will now be a new icon on the Planning board menu bar:

[Screenshot: LL APS]

This “*lightning bolt*” icon is the FR standard for APS, in this case, since we are on the Low-Level planning board, it is for the Low-Level APS, (Automated Planning System (LL)).

To configure a Low-Level ASP run, click on the drop-down arrow next to the “lightning bolt”:

[Screenshot: LL APS]

This will display the options available to the Planner:

[Screenshot: LL APS]

##### Run Manager

This will be where the Planner can see the Low-Level APS runs and their “scores”, (see Scoring below). Until there is a defined run setup and run then this will be blank.

[Screenshot: LL APS]

The Configure tab of the Run Manager allows the Planner to define the Scoring options and allow for the automatic updating of the Planning Boards that the Low Level APS run is ran against.

[Screenshot: LL APS]

The Scoring options available here are:

*No. Late Orders*

This option will score the Low Level APS run based upon the number of late orders and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with the least amount of Late Orders.

*No. Late Pieces*

This option will score the Low Level APS run based upon the number of late pieces and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with the least amount of Late Pieces.

*Percentage of Orders On Time*

This option will score the Low Level APS run based upon the percentage of Orders on time and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with the most amount of Orders delivered on time.

*Percentage of Pieces On Time*

This option will score the Low Level APS run based upon the percentage of Pieces on time and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with the most amount of Pieces delivered on time.

*Days Late*

This option will score the Low Level APS run based upon the number of days late and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with the least amount of days late across the planning board.

*Average no. of Product Changes*

This option will score the Low Level APS run based upon the average number of Product changes and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with the least average amount of Product changes.

*Average Efficiency*

This option will score the Low Level APS run based upon the average efficiency and will plan the Orders/Strips accordingly. Using these criteria will produce a Run with best average efficiency.

*Use all available scoring options*

Enabling this option will automatically disable all of the above scoring options and assume that they will all be applied to the Low Level APS run. By default, this option is enabled.

Additional settings

*Update planning boards in “real time”?*

Enabling this option will allow FastReact to run adhoc Low Level APS Runs and will update the planning boards periodically.

> **Note:** This will slow down the overall planning process.

*Output debugging to a log file*

This option should only be enabled with the approval of FRS as it will output a log file to help analyse issues with the Low Level APS Run.

*Scoring*

This option will allow the Planner to see the scoring for each of the above scoring options. Clicking on a particular scoring criteria will display a pop up dialog with the scoring results for the selected score criteria.

*Setup…*

This option will Allow the Planner to define the Low Level APS Run and assign sorting criteria:

[Screenshot: LL APS]

### Define

*Context: Functionality > Low Level APS › Low Level APS. › Define*

*Enter APS run name*

This will be the User defined name of the Low Level APS Run that is being configured. If no Low Level APS Run has been configured yet, this will be blank.

#### General

*Context: Functionality > Low Level APS › Low Level APS. › Define › General*

*Run description*

This will be the User defined name of the Low Level APS Run that is being configured.

*Use time fence*

This will open when enabled, will, along with the option below force the Low Level APS Run to take in to consideration Time Fencing.

*Time fence days*

This is the number of days that FR will time fence when running the Low Level APS run.

*Ignore progress check*

Enabling this option means that FR will ignore any production that has been done and may replan Order that are already in production.

*Max size*

This option will determine that maximum size a strip can be. This field is measured in ***Minutes*** and not order quantity or strip quantity.

*Max strip count*

This is the maximum split count that an Order can be split during the Low Level APS Run. This is normally used in conjunction with the above option.

*Continue build up*

The option will force FR to apply follow on Build Up Curves to the strips after Low Level APS has replanned the strips.

*Critical path check*

This option will either Ignore, use Critical Events or use All Events on the Critical Path. This means that the Low Level APS will take into consideration the CP when planning or replanning strips.

*Late delivery tolerance*

This will allow the Low Level APS run to plan Orders/strips with in a spesified number of days of the Orders delivery date.

#### Order sorting

*Context: Functionality > Low Level APS › Low Level APS. › Define › Order sorting*

This will tab will allow the Planner to define how the Low Level APS run handles the Order/Strip sorting.

There are a number of field sorting options:

- Product type code
- Product type UDF
- Product code
- Product UDF
- Customer code
- Customer UDF
- Order code
- Order status
- Order UDF
- Delivery/Required date
- Quantity

#### Row sorting

*Context: Functionality > Low Level APS › Low Level APS. › Define › Row sorting*

This will tab will allow the Planner to define how the Low Level APS run handles the Row sorting.

There are a number of field sorting options:

- Product type
- Product type efficiency
- Product
- Product UDF
- Order UDF
- Earliest strip start
- Earliest strip finish

#### Excluded rows

*Context: Functionality > Low Level APS › Low Level APS. › Define › Excluded rows*

This will tab will allow the Planner to define which Rows are to be excluded from the Run.

#### Configuration and Example

*Context: Functionality > Low Level APS › Low Level APS. › Define › Configuration and Example*

##### Example configuration:

General configuration

[Screenshot: LL APS]

In the above example, the FastReact Low Level APS Run has been created to plan in the Earliest Gap.

- Although time fencing is enabled, there are no time fence days set so FR will start planning from “today”, based upon the time fence start setting of “production”, ie the start of the Strip.
- FastReact will take in to consideration any production done on the Orders.
- There are no splitting of Orders configured so Orders will not be split.
- The strips will automatically have follow-on Build up curves applied.
- Critical Path will be ignored.
- The Late delivery tolerance is set to “0” so will plan as close to the Orders Delivery date as possible.

Sorting of the Orders/Strips

[Screenshot: LL APS]

The above setup will plan Orders/Strips based upon their Delivery Date in an ascending order.

Sorting of the Rows

[Screenshot: LL APS]

The above setup will sort the strips on each Row based upon the earliest date that athe strip can be planned.

#### Current Plan:

*Context: Functionality > Low Level APS › Low Level APS. › Define › Current Plan:*

Below is the current plan for the China planning board:

[Screenshot: LL APS]

Now run the Low Level APS:

The Low Level APS run that has been created will be available under the APS Lightning bolt on the Low Level plan:

[Screenshot: LL APS]

The resulting Low Level plan will now look like the below:

[Screenshot: LL APS]

Fast React has re-planned the China board. The planner can check “how good” this plan is via the **Scoring** option under the lightening bolt and selecting the “**All**” option:

[Screenshot: LL APS]

This **Scoring** will enable the Planner to make an informed opinion of the best Plan for that planning Board:

[Screenshot: LL APS]

As there is only one Low Level APS Run configured, there will only be one scoring entry. If the Low Level APS had multiple Runs configure the Planner could run the scoring and make an informed decision as to the best Low Level APS run to initiate.

Looking at the scoring for this Run:

[Screenshot: LL APS]

As can be seen using this Low Level APS run there are:

- 33 Late Orders
- 84021 Late Pieces
- 75.19% of Orders will be on Time
- 53.70% of Pieces will be on Time
- 90.23 Total number of days late on the Planning Board
- 9.60 Average number of Product Changes on the Planning Board
- 87.38% Average efficiency
