# Main Menu - Planning - Multistage APS

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > APS > Multistage APS
**Index keywords:** Multistage APS

---

## Multistage APS

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS*

### Run Multistage APS

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Run Multistage APS*

**Run Name:** This is the manually entered name of the APS run.

**Run Sequence (button):** Run the predefined APS sequence

**Cancel (button):** Cancel the APS run.

##### Execution Sequence

When the Run Name is selected the predefined sequence or activities that the sequence goes through will be listed in this box.

##### Progress

This list box will track the progress as the APS Run passes through each activity in the Execution sequence.

#### Setup

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Run Multistage APS › Setup*

This screen is where the sequence of activities that an APS Run goes through is defined or amended.

**Run Name:** This is the manually entered name of the APS run.

**Save (button):** Save the newly defined APS sequence

**Delete (button):** Delete the APS run.

##### Sequence of execution

When an activity to run has been selected it will appear in this list box.

##### Select a section

Select the section that the APS Run will be against.

##### Select an activity to run

This is a list of the available activities that can be selected to make up the APS Run:

**Create SWO for this section:** This activity will create Speculative Works Orders or SWOs where required.

**Run APS profile:: ?:** This activity will run a specific APS profile.

**Run materials calculation:** This activity will run a standard MRP calculation.

**Run materials calculation for MPS:** This activity will run the MPS MRP calculation.

### Aps

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Aps*

This button allows the user to run one or more execution plans (described below) and see the results for each.

###### Running APS

To run a single plan just click on the button marked 'Run highlighted plan'. The plan selected in the list (i.e. highlighted) will be executed.

To run multiple plans you must check each one in the box to the left of its name. The highlighted plan will be ignored. Then click on 'Run all selected plans'. Each plan will be executed in turn and return a result. Any reports that you have associated with the plan will be run automatically between executions.

If you want execution plans to run in a specific sequence then you should organise this by naming plans accordingly. As the plans are run in alphabetical sequence, prefixing with '01', '02', '03' etc will force a specific sequence.

###### Saving results

FastReact will allow you to save the new plan so that it becomes available to all other network users, or you can choose to not save it. In either case the results will be available on the planning board and in reports for you to review. (If the results are not saved they will be available during the current FastReact session. Once you close and reopen fast React the temporary results will be lost).

FastReact will check to see that plans are not in use before starting the APS run. If they are then you will be allowed to continue but the Save option will be disabled. This will prevent APS overwriting other user's efforts. If the plans are not in use when APS starts it will prevent other users making changes until it has finished.

**Score:** This column shows the results of the scoring calculation where a high value is a 'better' plan (The Planner defines what 'better' means). The best of multiple execution plans can be chosen to run and the results saved.

**Run highlighted plan (button):** This button will run the chosen APS plan.

**Run all selected plans (button):** This button will run all of the chosen APS plans. This button is only available if there is more than one plan.

### Define execution plan

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Define execution plan*

FastReact will allow the Planner to define a number of execution plans with different properties. The results of these plans are calculated using a common scoring policy so that the Planner can select the best one for the live plan.

**Execution plan:** Give the plan a name of up to 15 characters long. Plans are executed alphabetically so the Planner might want to force a specific sequence with the naming convention, although this is not really necessary.

#### User options

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Define execution plan › User options*

This tab holds options that you might want to change often.

**Soft constraints:** By default all constraints are considered to be finite or hard. APS will not allow finite capacity items to be overloaded or will not allow a plan which would result in materials shortfalls. Set constraints as soft as required as described above.

**Critical path:** You can plan how APS will attempt to plan the strips so that overdue events are concidered. There are a number of options to control this:

**Allow overdue events:** Ignore overdue events when planning the strips.

**Prevent overdue critical events:** Only events that are marked as critical will be taken into consideration when planning the strip.

**Prevent all overdue events:** All events are taken into consideration when planning the strip.

**Planning policy:** You can plan orders ASAP or JIT There are a number of options to control this:

**As defined on order:** You can force JIT for an individual order (defaults to ASAP).

**As defined by order status:** You can set each order status to have its own configuration of ASAP or JIT. There is also a Default option, which will take settings from the order as above. The ASAP/JIT by order status configuration is made on the General settings tab.

**Force all ASAP:** Irrespective of the settings above, all orders will be planned ASAP.

**Force all JIT:** Irrespective of the settings above, all orders will be planned JIT.

**Loading policy:** You can tell FastReact to load groups in different ways. This option will apply where you have a number of groups that can handle a specific product or range of products. If left unchecked FastReact could load one group right to the end of the planning calendar and leave other groups with no work. Clearly this would be unacceptable. To overcome this there are a number of different loading policies available.

**Equalise loading:** This (default) option will attempt to fill equivalent groups equally so that they run out of work on a similar date. This option might be best if the groups were your own factories and the cost of downtime would be high.

**Maximise efficiency:** FastReact will load up the most efficient (based on its efficiency profile) group first and then lower efficiency groups. If an order cannot be loaded into the most efficient group (because of late deliveries or other constraints) then it will be loaded in the next best group and so on. If it had tried all groups and still could not load within the required deliver it will plan the order in the group which gives the best delivery performance, irrespective of efficiency.

#### Other options

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Define execution plan › Other options*

FastReact provides a range of other options to allow you to fine tune you planning policy. These are:

**Prevent order fragmentation:** When planning orders around previously planned (higher priority) or existing fixed orders it may be possible for APS to start to plan an order on a specific date but then find that there is no capacity on subsequent dates as it had already been consumed by other orders. This would leave a gap in the order continuity. This may be undesirable.

- OFF - With this option turned off the order will be started where there is capacity available but this may be followed by a break, or breaks, in production continuity where the capacity is already filled by other orders. This option would provide a full plan as any small 'holes' would be filled, but it could give a fragmented production plan for individual orders.
- ON - With this option enabled orders will always be planned without gaps caused by intervening orders. This would offer continuity of production on any order but could result in production gaps and lower overall loading.

**Consider Work In Progress:** The planned operation (shown on the planning board) may be preceded by one or more feeder operations. When calculating the earliest possible starting date for any order, APS will need to consider the factors below.

> The Throughput time associated with the planning Group. This is the time taken (in days) from feeding work into the planned operation to when it is expected to come out again. This is the planned operation's Work in Progress. This assumes that the strips on the planning board show work coming OUT of production. If strips represent feed into production then the Throughput time for the Group should be set to zero.

> The Accumulated offset days between feeder operations to build up the total number of days between the start of the strip and each operation. The days are group specific using the Preparation and Standing time against each operation in each group. Times for operations that are entirely complete will be ignored. The calendar attached to the group and specific operation is used to calculate these offset days.

> The Progress to date on any operation so that the planning of the main operation can continue whilst eating into the progress on feeder operations. If the progress is zero then the full number of allowed days (above) must be taken into account, but with positive progress planning can start earlier by consuming quantities already made on these feeder operations.

Strips which have already been started in production will not take account of any of this logic as their start date will have been determined by the date on which production was last updated and they will not be moved from this date. However, they must consume progress in feeder operations in exactly the same way as orders still to be planned. One difference is that any progress on strips which have been started must be added back into the feeder operation progress.

**Do not allow order Production to start before it's APS Base Date (select only one):** An earliest start date can be defined for each order and APS will respect this date. This allows the Planner to override the normal calculation to prevent earlier planning, however, APS may well have to plan later than the specified date. The Planner could use this to delay the start of an order beyond that which APS would consider necessary. Orders will still be planned in priority sequence.

**Do not allow order Preparation to start before it's APS Base Date (select only one):** An earliest start date can be defined for each order and APS will respect this date. This allows the Planner to override the normal calculation to prevent earlier planning, however, APS may well have to plan later than the specified date. The Planner could use this to delay the start of an order beyond that which APS would consider necessary. Orders will still be planned in priority sequence.

**Do not allow planning beyond the Order Stock Out Date (ASAP plan only):** A Stock Out Date can be defined on the Order. This option allows the Planner to prevent the order being planned past this date in Low Level systems only.

**Replan manually locked strips if material problem:** Planners can manually lock strips and these will not be moved by the APS run. This option will allow the APS run to unlock and replan the strip if there is a material problem.

**Allow manually locked strips to be re-planned:** If this option is selected, APS will ignore the manual plan lock on a strip and allow it to be re-planned.

**Pool material locations:** This option will pool the same material from different locations.

**Consider SWO material products to be available as materials:** APS created SWOs, which are materials for Confirmed Orders, will be available regardless of their stock position.

**Do not replan orders for material products:** This option prevents the replanning of material products.

**Unload all orders for non material products:** This option will unload all non material products.

**Do not save material results from this run.:** Any MRP results generated from the APS run will not be saved.

**Use default strip length with Soft Primary and Secondary capacity and JiT policy:** **Use the predefined strip length when JiT planning (High Level).:** **Use default strip length with Soft Primary and Secondary capacity and ASAP policy:** **Use the predefined strip length when ASAP planning (Low Level).:** **Re-plan fixed strips if material problem:** Normally fixed strips will not be moved. However, if there is a materials shortfall you may want these strips to be re-planned later so that they will be supported by materials.

> **Note:** Strips which are on a low level planning board will never be moved.

Strips which have started production will not be moved unless the order has been flagged to allow this (Order is on hold).

**Capacity Scaling:** The Planner may want large orders to consume more of the Group's capacity than smaller orders. This can be ensured by specifying a maximum target length for any order and APS will attempt to achieve this by using as much capacity as required up to the maximum available in the group.

> **Note:** Set this value to 1 to turn off Capacity Scaling.

#### Priority formulae

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Define execution plan › Priority formulae*

FastReact has a number of pre-defined priority formulae. It uses these to determine the sequence in which orders will be placed in the overall plan.

> **Note:** Orders that are fixed in any way will always have the highest priority.

**Plan in delivery date sequence:** Earlier delivery dates will be give a higher priority than later ones.

**Plan in 'Plan line' priority sequence:** FastReact will use the same algorithms as it uses in its Plan Line calculation to determine priority. This is only available if you have the Plan Line licence option.

**Plan in order priority sequence (lower value = higher priority):** Lower priority values will be given a higher priority than higher ones.

**Plan in Status/Delivery date sequence:** FastReact will plan the orders in status then delivery sequence.

**Plan in Delivery date/Order status/Product priority sequence:** FastReact will plan in Delivery date, Order Status and then product priority.

**Plan in Order status/Delivery date/Product priority sequence:** FastReact will plan in Order Status, Delivery date and then product priority.

#### Reports

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Define execution plan › Reports*

FastReact can be instructed to run selected reports after each execution plan has finished. Having selected the reports to run, the automatic report option will also need to enabled. See below.

#### Unattended execution

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › Define execution plan › Unattended execution*

FastReact can run specific execution plans at a particular time of the day. The user 'service' must be logged on as only this user has rights to run any automatic function. Where several plans are set to execute at the same time they will be run, one after the other, in alphabetical sequence and the plans saved. All reports will be valid if run automatically between executions. If you want to leave FastReact with any specific plan then it must be the last one to be executed. Make sure this is the case by the naming convention you use.

### General settings

*Context: Main Menu > Planning > APS > Multistage APS › Multistage APS › General settings*

This tab offers settings that are global across all execution plans.

**Select method of scoring:** FastReact provides a variety of ways to score the results of a plan. That is to put a numeric value on the benefit of the plan solution. These are:

**Number of strips fully planned on time for delivery (M1):** This is the number of order/deliveries that will fully meet the customer's delivery date. If the strip has even a single item late for delivery it will not be included.

**Quantity fully planned on time for delivery (M2):** Similar to the above but this will also take account of the quantity on each order/delivery.

**Quantity fully or partially planned up to the delivery date (M3):** This will include order/deliveries which are part late for delivery and will add in those items which will be available to meet the customer's delivery date, but exclude those that will miss it.

**Value fully planned on time for delivery (M4):** This will take the value (selling price of the order) multiplied by the quantity defined in M2 above.

**Value fully or partially planned up to the delivery date:** This will take the value (selling price of the order) multiplied by the quantity defined in M3 above.

##### Vendor date link point

**Arrive at customer:** The vendor linking point will be the date that the Order arrives at the customer.

**Complete in factory:** The vendor linking point will be the date that the Order is complete in the factory.

**Ship from factory:** The vendor linking point will be the date that the Order is shipped from the factory.

**End of plan:** The vendor linking point will be the end of the plan.

##### Confirmed/Provisional/Speculative/Transit

You can force orders to be planned ASAP or JIT in a number of different ways. One method is to make the setting based on the order status. You can set ASAP/JIT or Default for each order status here. The Default option will take the value defined on the order itself.

**default:** Plan the Order based on its delivery date and any other ASP set options.

**As soon as possible:** Regardless of the delivery date, plan the Order as soon as possible as long as its not late.

**Just in time:** Regardless of the delivery date, plan the order so that it is delivered just in time.

##### Settings apply to all execution plans

##### General options

**Always use the default route for work content:** FastReact allows you to define a number of different routes for different supply methods. You can tell FastReact to always use the work content from the default route and ignore work content that may be entered in other routes.

**Skip materials calculations:** This option will allow a planning run to be performed but bypass any materials calculations, irrespective of the settings for finite/infinite materials constraints. It is primarily used for testing.

**Roll back materials consumed beyond their lead time:** This option will roll back materials consumed beyond their lead time

**Always pool materials at different locations:** This option will pool all the locations together so that APS only has one pool per material.

**Allow manual materials calculation after APS:** This option will allow planners to run manual MRP calculations.

**Ignore product properties:** FastReact will make decisions on where to plan orders by means of various property matching criteria. The Planner may want to disable this option, primarily for testing purposes.

**Ignore order properties:** As above but for Orders.

**Unload orders that do not have materials defined:** You may want FastReact to ignore those orders that do not have a valid bill or materials attached (Valid in this respect means that there is at least one material defined, or no materials are actually required). These orders will be returned to the High level planning board Load list. Any orders that are planned at low level or, by virtue of their order status do not need materials, will be included irrespective of this setting.

**Run reports after completion of each execution plan:** This options turns on the ability to run reports after the execution plan run has completed.

**Print selected reports:** Unless selected any automatically run reports will only be sent to a text file..

**Generate analysis report of failed orders:** This option tells APS to generate a text file which can be used to see why orders were not planned. The time taken to produce this file is small so it can be turned on with little performance degradation. The file will be held in the LogFiles folder and will be called 'AP' followed by the execution plan name.

**Generate analysis report of planned orders:** This option tells APS to generate a text file which can be used to see which orders were planned. The time taken to produce this file is small so it can be turned on with little performance degradation. The file will be held in the LogFiles folder and will be called 'AP' followed by the execution plan name.

**Warn if close without saving plans:** FastReact will warn you if you close the APS dialog without saving your new plan. The Planner can then chose to save the changes or abandon the new plan.

**Materials calendar:** FastReact expects the lead times for materials to be in calendar days. If you are importing this data from another system in working days you can use a calendar to convert these working days into the calendar days that FastReact needs. Select (none) to disable this function.

**Time fence:** FastReact is able to construct a new plan very quickly based on existing and changing data. However, this plan needs to be turned into production by suppliers or your factories. To achieve good performance they will want a stable plan with as few changes as possible in the short term, with longer term changes having little impact on day to day operations.

Thus the main objective of the Time fence is to provide suppliers with this stable, short term plan. To achieve this, the Time fence function will allow planned orders to be effectively locked in place (both in time and planned location) during an APS planning run. By locking orders you are telling FastReact to ignore any capacity or materials problems, relying on local management to resolve these issues.

You can define the Time fence period to suit your own situation with longer periods giving more stability but possibly a less achievable plan (capacity overloads, material shortfalls).

##### General rules

The following general rules apply to the Time fence function:

**Global:** All rules are global in nature in that they cannot be defined for individual execution plans. The time fence must be enabled manually; it cannot be enabled or disabled on a schedule.

**Period:** The time fence period is defined in calendar (not working) days and will run from the start of the APS plan. This will be either Today or the Start of the current week. This is defined in Main menu - Setup - Configure - Planning on the High Level tab.

**Order status:** The time fence rules may be applied, or not, for each different order status, the time fence period must be the same for each status, however.

##### Planning rules

The following rules are used to determine whether an order can be moved and if so what will its range of movement.

###### Rule 1

If an order is currently planned to start before the start of the APS plan and will finish inside the time fence period then any overhanging planned quantities will be accumulated into the first available day. In this way any shortfalls in production will not be re-planned but show as an overload on that supplier. This will provide a good visual check that suppliers are performing according to the plan and avoid slippage that could occur if the plan is constantly revised to accommodate poor performance.

###### Rule 2

Any order that starts on or after the APS start date but is planned to finish on or before the time fence period will not be moved even if there are capacity or materials problems. This could result in the plan becoming overloaded. This provides stability in that any order that is currently planned in a supplier will remain at that supplier.

###### Rule 3

Any orders that start before the time fence period but end outside of the time fence will be available for Re-planning by APS. If there are capacity or materials problems this could result in these orders being moved to outside the time fence period. This will allow for a measure of smoothing of the plan allowing later orders to be moved to achieve a better plan.

###### Rule 4

Any orders that are currently planned outside the time fence period can be re-planned, but APS will not move these earlier than the time fence. This will prevent new orders from unexpectedly appearing on a supplier.
