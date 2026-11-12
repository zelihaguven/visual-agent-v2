# Main Menu - Setup - Configure - Planning (part 1)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > Planning
**Part:** 1 of 2 — sections: Planning Board Options, Configure, Options, Strip hints, Order optimise loading and Product optimise loading, Strip stage marker, Minimum Order Increase, Pla...

---

## Planning Board Options

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options*

The entries in this dialog allow configuration of global planning values.

### Configure

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Configure*

**Time fence days:** In certain configurations of FastReact the current plan can be sent to a remote site, for example a plan made at a central location can be sent to the production factory. The factory can then send back production progress. To ensure the local plan is not altered after it has been sent to the factory, 'time fence' can be used. Orders on the plan that are within the specified number of days from 'today' will be immovable. If this is set to 7 days then orders that start within the current week cannot be moved.

**Early warning days:** FastReact can display a warning on a strip if it is planned too early for delivery to the customer or to a subsequent process/section. The number of days that define 'too early' are specified here. The number of days early is the difference between the availability date (to next section) and the 'preparation' date required by the next section. For the final section this becomes the difference between the Order delivery date and the strip available to customer date. This will help to identify any strips which could be moved at least 'x' days later without an availability issue and could help to reduce inventory. The warning is a diagonal black line on the upper right corner of the strip. This can be disabled by setting the warning days to zero.

**Equalise Order Multiplier:** Used in conjunction with the Right Click Equalise function, this option will factor the value in to the split strips.

#### Options

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Configure › Options*

**Extra data verification on load:** When enabled FastReact will perform additional data verification when you load the plan. This will make the planning board a little slower to open as FastReact check the data integrity.

**Data logging on planning board save:** When enabled, this option will log all the data on a planning board when it is saved.

**Allow Low Level rows to have multiple sections/widths:** In order to calculate the time taken to produce an Order FastReact will use the Order quantity, the Product work content and the capacity of the resource producing the order. In certain circumstances this is not enough as production times can be considerably reduced by parallel production.

For example, a weaving loom of 100 cm width could be making an order for fabric of 33 cm wide. It might be possible for the loom to make 3 widths of fabric across the loom with dividers to split the overall width into 3 or for the fabric to be cut after weaving. In this case the weaving time would be only a third of the normal time. The section width divided by the Order width will give the number of pieces across a section. FastReact will multiply this by the number of sections to give the number of pieces produced simultaneously across the machine.

**Load strips in selected sequence (defaults to delivery date sort):** This option will allow the selection of multiple strips either from the Low Level or High Level planning board and plan them on a single row in the order that they were selected.

**Show completed strips in Low Level Row strip list:** Normally when strips are completed on the planning board you loose visibility of them on the planning board. This option allows you to see where the strip was planned when it was completed.

**Add increased order quantities to existing Low Level strips:** Enable the check box to allow FastReact to automatically plan additional quantities to orders already planned, for example when a customer increases the required quantity. This can be undesirable as a large increase to a planned Order will affect other Orders that are planned subsequently. When disabled any increases to the Order quantity will be placed in the Load list for manual planning. If there are no strips on the board then the additional quantity will be added to the load list.

**Enable drop down style Low Level planning board:** Enable the check box to allow the user to view the planned Orders as a vertical list below each planning Row. For more information please read additional documentation relating to Low Level planning boards.

**Show row capacity factor x calendar hours x capacity:** The capacity factor is normally displayed on low level planning board rows. There may be times when this factor should be multiplied by both the calendar hours on each day and by the actual row capacity. This will give a real capacity value rather than the capacity factor.

**Show "Last product type" indicator on low level rows:** This option will colour up the left hand side of the Low Level row with the colour of the product type for the last strip planned if that product type has a colour defined on its setup.

**Do not calculate Total Days Early for each row (speeds up loading):** This option will not calculate the days early and hence not populate the Early Days field.

**Hide Confirmed orders in low level load list and order accept option:** FastReact always displays all orders in the load lists and order except lists. When this option is enabled orders that are of status Confirmed will not be displayed in the load lists.

**Hide Provisional orders in low level load list and order accept option:** FastReact always displays all orders in the load lists and order except lists. When this option is enabled orders that are of status Provisional will not be displayed in the load lists.

**Hide Speculative orders in low level load list and order accept option:** FastReact always displays all orders in the load lists and order except lists. When this option is enabled orders that are of status Speculative will not be displayed in the load lists.

**Hide Transit orders in low level load list and order accept option:** FastReact always displays all orders in the load lists and order except lists. When this option is enabled orders that are of status Transit will not be displayed in the load lists.

**Hide MPS Suggested orders in Low Level load list and order accept lists:** The option does exactly as it says, it hides suggested orders in the Low Level load and accept lists.

**Use Grid style load list:** The option will allow the planned to use the more functional Grid style load and accept lists. This option must be enabled for some of the more advanced functionality to work, i.e, Substitution and Collaboration Rejects.

**Use prep start calendar:** This option allows the planner to use the Prep start of the planned strip instead of the event Base Date.

**Allow load list to be constantly open when planning:** This option allows the Planner to keep the Low Level load list open when planning. If this is not enabled the Load List will close each time a strip is planned.

**Realign strips to production date after production update:** When enabled any updated strip will be realigned with 'today's' date. FastReact assumes that production figures will be entered retrospectively on a daily basis. It is therefore logical to place all updated strips in line with today to reflect the up to date position of production in the factory. This will save any manual adjustment of the plan after update (inevitable since actual production very rarely matches the plan).

This is undesirable if you update production hourly or weekly. Alternatively many planners prefer to see the over/under production of each line before realigning updated strips so that they can keep a feel for the performance of their production resources and even to adjust planned capacities if large difference occur regularly.

**Enable group/customer profiles:** This option will enable the functionality to prevent loading an Order oh High Level or Low Level boards based upon Customer.

**Smooth operation schedules:** This option allows the application of different calendars to different operations.

For example, cutting works 5 days a week on a cutting calendar and sewing works 7 days a week on a sewing calendar, this option will allow for the transition between one calendar and the next.

**Enable group/efficiency profiles:** An group/efficiency profile is a table of Product Types with an associated efficiency factor. Each Row (Low Level planning) and each Group (High Level planning) can have an Efficiency profile attached. When an Order is planned on the Row/Group the efficiency factor for the associated Product type will be applied.

For example, in apparel manufacture, Line 1 may produce shirts at 85% but jackets at 60% where as Line 2 efficiencies may be 80% and 70% respectively. In this way each Row /Group can be given a specific profile. In reality one profile may apply to several Rows/Groups.

Enable the check box to switch on this functionality.

**Enable work in progress monitoring:** This option enables the monitoring of non planned schedules and updates to identify where the supply from these operations is insufficient to fully support the planned schedule.

**Planner cannot change Standing time for normal operations:** The flow of any one item through a process is normally defined according to the process itself.

For example, in apparel cutting takes place 3 days before sewing, finishing takes place 2 days after sewing etc. This throughput can be set as a default but also altered to suit each different product (e.g. goods may or may not require embroidery, hence cutting could be 7 days or 3 days before sewing).

On occasion there may be sufficient capacity to plan the goods in the key stage (operation) of the process but cause a bottleneck at an earlier or later unplanned stage (operation). In these circumstances altering the standing time for each operation could alleviate the load on pre and post-planned operations by pushing the load backwards or forwards in time.

Enable this check box to prevent planners being able to alter standing time for normal operations.

**High Level Planner cannot change Planning board for order:** Orders are allocated to one of the defined planning boards. Once this has been done the Order must be 'de-allocated' from this plan before it can be placed on a different board. Enable the check box to prevent the planner from performing this function (e.g. for security reasons).

**Allow orders to be split across low level planning boards:** This option allows the user to split an order across Low Level planning boards.

**White out non matched strips planned from load list:** This option will "white out" any strips on the planning board that do not match any of the selected Load List strips. This will allow the planner to see instantly where like strips are planned.

**Operation move time by Product (defaults to Orders):** The time taken for work to move from one operation to the next is normally defined for each order, however the planner may prefer this to be product based. This preference can be selected here.

**Show product description on load list (defaults to Order):** Enable this option to see the product description on the load list. By default the Order description will be displayed.

**Show delivery reference on strips:** With this option enabled the delivery reference, entered in the order delivery schedule, will be shown appended to the order reference on planning board strips and in reports.

**Show order description on strips:** With this option enabled the order description will be shown appended to the order reference on planning board strips and in reports.

**Show product description on strips:** With this option enabled the product description will be shown appended to the order reference on planning board strips and in reports.

**Show day numbers on date scale (Monday=1):** Normally FastReact displays the actual day of the week on the date scale on the planning board. With this option enabled the day of the week is replaced with a number that corresponds to the day in the week.

e.g. Monday = 1, Tuesday = 2 etc.

**Review statistics before saving plan:** When enabled, this option will cause the Statistic dialog to appear when the planning board is being saved. This allows the planner to review the changes and effects of these changes on the whole planning board.

**Earliest load date = 'Today' if no o/s events (defaults to load date):** With this option enabled the earliest load date displayed on the planning board will be 'Today' for all strips.

**Do not show all sections when loading new orders:** Only valid sections for the selected order will be available.

**Turn on linked order relationships:** This option enables Linked Order Relationships.

**Respect group/operation enabled status:** This option will force the recognition of the enabled flag on the Group - Operations setup dialog at Low Level.

**Use managed consolidation option & criteria:** If this option is enabled then a Consolidation tab will be available under Setup - Configure - Planning. Enabling this option will disable all "legacy" consolidation settings from load lists and planning boards.

**Enable advanced order set functionality:** If this

**Enable pop out strip hint:** If this option is enabled the Pop Out Strip functionality will be enabled. Enabling this option will disable Strip Hints.

#### Strip hints

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Configure › Strip hints*

This contains three options. FastReact can display some order details and any strip notes in a hint box when the cursor is placed over a strip on the board.

**Delay time before display (1/10 Sec):** This specifies how long after putting the mouse on a strip before the hint box first appears

**Display time before hiding (Sec):** This specifies how long the hint box remains on screen. Moving the mouse will automatically hide the hint box.

**Display:** Enable a selection of the below check box to have the selected strip notes appear within the hint.

- **Order description:** - **Product description:** - **User defined strip display:** - **Strip notes:** - **Order notes:** - **Contract quantity:** - **Deliver to:** - **Extended delivery date:** #### Strip highlighting

FastReact can to highlight all strips on the board that have the same properties as the strip under the cursor. The planning board must be rotated to show the relevant view. The rotations are:

**Orders:** Enable this box to highlight all strips with the same Order reference. Linked orders (::) will also be highlighted. The board should be rotated to show 'Order' view.

**Products:** Enable this box to highlight all strips for the same Product. The board should be rotated to show 'Product' or 'Product details/Order colours' view.

**Product type:** Enable this box to highlight all strips for the same Product Type. The board should be rotated to show 'Product Type' view.

**Customers:** Enable this box to highlight all strips for the same Customer. The board should be rotated to show 'Customer' view.

**Deliveries:** Enable this box to highlight all strips for the same Delivery. The board should be rotated to show 'Delivery' view.

**User defined:** Enable this box to highlight all strips for the same User defined value. The board should be rotated to show 'User defined' view.

**Order sets:** Enable

#### Order optimise loading and Product optimise loading

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Configure › Order optimise loading and Product optimise loading*

Optimise loading is used as a way to help the planner load the planning board following certain criteria such as width of machine. When enabled, there will be an Optimise tab on the Order / Product entry dialog.

For example, if a weaving loom has a width of 150cms, you could set two optimise loading factors:

- Maximum width
- Minimum width

Values for these factors can be set for both Orders/Products and planning Rows. These values are compared following a set of rules e.g. equal to, greater than, less than, etc. FastReact can then visually warn or even prevent loading altogether if these rules are broken.

The options are:

**Disabled:** Optimise loading is disabled.

**Warning Only:** Optimise loading is enabled but will warn visually of any optimisation problems.

**Prevent loading:** Optimise loading is enabled and the planner will not be able to plan orders on production Rows where the optimise rules are broken.

#### Strip stage marker

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Configure › Strip stage marker*

This option will put the name of the Planned Operation that the strip belongs to onto the strip so it can be seen on the strip.

The options are:

**Off:** No operation label on the strip.

**Stage name:** The operation (stage) name will be on the strip.

**Short code:** The operation (stage) name short code will be on the strip.

#### Minimum Order Increase

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Configure › Minimum Order Increase*

This option will allow the user configuring the system to define a percentage of an Order increase which will be automatically be assigned to a planned strip. This option requires the option Add increase to planned strip to be enabled. FastReact will look at the total Order quantity and apply the percentage to that

Example,

Order quantity = 1000 units

Minimum Order Increase % = 50%

So any increase of 500 units or less would automatically be added to the planned strip. If the increase is for 501 or more then, 500 would be planned and 1 would be in the load list.

### Plan colours

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Plan colours*

One of the main benefits of FastReact is the highly visual nature of the planning board. Colour is used extensively to warn the planner (or any user) of potential problems. FastReact has a pre-configured set of colours to define problem conditions. These colours may be changed, but we would strongly recommend that the colours are left as per the defaults unless absolutely necessary.

The meaning behind the default planning board colours are shown on the dialog but for further details on their meanings please refer to Strip colours.

Colours can be changed by clicking on the small coloured box to the left of each description. Make sure that combinations of colours do not obscure data, for example by having red text on a red background. The default colours have been carefully selected to avoid this issue.

**Reset defaults (button):** - [Icon: Reset Value] Click to reset defaults

The restoration of the system default colours are accomplished by clicking this button.

### Calendar

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Calendar*

#### Week ending day

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Calendar › Week ending day*

Specify the week ending day for the planning board and all reports. Daily production updates will be consolidated into weekly figures according to the day specified.

#### High level plan calendar extent

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Calendar › High level plan calendar extent*

This section is used to define the number of weeks (forward and backwards from current week) that FastReact displays on the High Level planning board.

**Planning forward weeks (12-150):** Set the number of weeks forward from the current week that you want to view.

**Planning history weeks (1-13):** Set the number of weeks prior to the current week that you want to view.

### Loading bar charts

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Loading bar charts*

Bar charts are typically used in FastReact to show the load versus capacity on the unplanned operations. This is also frequently referred to as 'bottleneck' management. These same warning limits are also applied to the High level planning Loading charts

#### Warning limits

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Loading bar charts › Warning limits*

The bar charts can be configured to highlight loading issues between certain user defined levels. This dialog enables you to configure those levels

**Less than:** This will highlight the bar chart load if it falls below the defined percentage.

**Greater than:** This will highlight the bar chart load if it is above the defined percentage.
