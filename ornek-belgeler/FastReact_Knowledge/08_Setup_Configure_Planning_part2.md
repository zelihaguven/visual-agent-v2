# Main Menu - Setup - Configure - Planning (part 2)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > Planning
**Part:** 2 of 2 — sections: High level, Options, Colours for order status, Manual entry of schedule quantities, Customer for suggested orders, Default rule to be used for new products, ...

---

### High level

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level*

#### Options

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Options*

This series of check boxes determine how the high level planning board will behave.

**Do not force daily strip alignment:** Under normal conditions the High level planning board will automatically align planned strips to the nearest whole day. When enabled this option will allow High level strips to be started part way through a day.

**Force plan to weekly boundaries:** This will force all strips planned on the High Level planning board to start on the first day of the week, regardless of where you place the strip. This option overrides any setting on the 'Do not force daily strip alignment' option above.

**Auto scroll planning board:** When enabled the high level planning board will automatically scroll up or down in line with your current mouse position.

**Use Grid style load list:** With this enabled the HL board will use the Grid style Load and Accept lists.

**Allow strips to be split with the mouse:** By default strips at high level cannot be split. However with this option enabled you will be able to right click on a high level strip and split a desired quantity off the strip and plan the balance elsewhere on the planning board.

**When splitting strips retain any user entered schedule:** When enabled, this option will allow the retention of any user entered schedule set against the order.

**Add increased order quantities to existing High level strips:** When enabled any increase to Order quantities will automatically be added to existing strips on the high level planning board. If no strip exists then the additional quantity will be added to the load list.

**No capacity available before 'today’:** If this option is enabled then there will be no capacity earlier than today. When disabled, capacity is available from the start of the current week.

**Enable JIT autoloading:** To help allocating orders to the correct factories you can set FastReact up to auto load orders to specific factories by using properties. With this option enabled FastReact will locate suitable factories based on the properties and load the orders to a JIT basis.

**Only allow JIT autoload of Load List orders:** FastReact has the facility to JIT (Just In Time) plan orders. With this option ticked, in conjunction with the above option to "Enable JIT autoloading", FastReact will allow the planner to select which orders to autoload via the High Level Load List.

**Allow JiT alignment of planned strips:** This option will allow the Planner to JiT already planned oders as well as the order that are not planned.

**Separate load for low level plans:** The high level loading charts may show the load from low level plans in a different colour to the load from orders planned at high level only.

**Separate load for Confirmed orders:** The high level loading charts may show the load from confirmed orders in a different colour to the load from other orders.

**Separate load for Provisional orders:** The high level loading charts may show the load from provisional orders in a different colour to the load from other orders.

**Separate load for Speculative orders:** The high level loading charts may show the load from speculative orders in a different colour to the load from other orders.

**Separate load for Transit orders:** The high level loading charts may show the load from transit orders in a different colour to the load from other orders.

**Separate load for Suggested orders:** The high level loading charts may show the load from suggested orders in a different colour to the load from other orders.

**Separate load for Reservation orders:** The high level loading charts may show the load from reservation orders in a different colour to the load from other orders.

**Draw utilisation markers on bar charts:** When enabled, this option adds a Target efficiency field to the Group setup dialog.

**Hide build up option on strip menu:** Do not show the option to change either build up curve or change time on the high level strip menu.

**Show supply window:** The high level planning board can optionally show the acceptable window in time into which orders can be loaded. See High level planning board details.

**Sourcing strip display (defaults to manufacturing):** This style of display hides much of the detail that is useful to manufacturing planning, but is of little relevance to planning suppliers.

**Show pre-production extent:** This displays a coloured block that shows the date of the earliest incomplete critical path event.

**Filter groups that have valid costings:** This option, when enabled, will show only those orders or products that have a costing. They will also be sorted on the board so that the highest preference is at the top. If there are no costings for any group then all groups will be shown with a warning of "No Data".

**Do not hide fully updated strips:** This option, when enabled, will show a green square where previously completed orders were planned.

**Reverse stage sort sequence:** This option, when enabled, will reverse the stage sequence of the multiple strips on the planning board.

**Use expanded mode:** This option, when enabled, will increase the size of the left hand section of the Planning board.

#### Colours for order status

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Colours for order status*

Colours can be selected for the text that appears to the left of the strip on the High Level planning board. Orders of different status can have a different colour for easy identification:

- **Confirmed:** - **Provisional:** - **Speculative:** - **Transit:** **Background (button):** The user can set the background colour of the high level planning board. The default colour is white.

**Minimum visible strip length (pixels):** This defines the minimum width that a strip will be displayed on the planning board. This can be useful if you have a lot of small quantity strips.

**Default initial strip length (days):** This defines the default number of days for a strip when first loaded onto the High Level planning board.

**Numeric chart display precision:** This defines the decimal places to be displayed for the numeric display of the High Level planning board.

#### Manual entry of schedule quantities

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Manual entry of schedule quantities*

When typing in a schedule for a strip on the high level planning board FastReact displays the periods as daily, with this option enabled the periods will be set to weekly buckets of time. The choices are:

- **Daily (default):** - **Weekly:** - **Monthly:** ### MPS

This option will only be available if you have the plan line functionality enabled.

#### Customer for suggested orders

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Customer for suggested orders*

This is a list of all the customers in the system.

#### Default rule to be used for new products

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Default rule to be used for new products*

With this option set, new orders will be defaulted to one of the below options:

**Maximum of Customer orders or Forecast:** **Forecast orders only:** **Customer orders only:** **Customer orders if non zero else Forecast:** #### General configuration

**Demand period:** Daily, Weekly or Monthly. The timescale for the Demand.

**Forecast period:** Daily, Weekly or Monthly. The timescale for the Forecast.

**Stage to process:** which operation (stage) to process.

> **Note:**

> **This stage can be overridden when running multi stage APS and will use the final stage in the e:**

> **selected section.:**

#### Options

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Options*

**Consider delivery date for confirmed orders (default treat as stock):** **Use earliest demand date for SWO delivery date:** The Suggested Works Order date will be the earliest delivery date of the confirmed orders.

**Allow MPS to set the Product Customer on Suggested Orders:** This option will allow the MPS module to set a pre-defined customer against all Suggested Orders.

**Debug to file:** Enabling this option will create a Debug log in the Fast_React folder. This should only be enabled with the approval of FRS.

**Update above configuration (button):** This button will update any changes to the above MPS configuration changes.

#### Section configuration

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Section configuration*

**When calculating section:** This will list all the planned sections in the FR system. The Planner can then set individual options (below) for each of the sections.

#### Options for selected sections

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › High level › Options for selected sections*

**Calculate from demand table:** This licence option will allow the user to calculate MRP from imported values.

**Demand from MRP from section:** Demand is generated from the more traditional planning of the order.

**Update section configuration (button):** This button will update any changes to the above section configuration changes.

### Rotation

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Rotation*

[Screenshot]

A Rotation tab has been added for the configuration of Planning Board Rotations, the left hand list are the rotations available but not currently in use and the right-hand list are the rotations currently in use (they rotate in the order of the list).

[Screenshot]

New custom rotations can be added by typing their name into the left hand text entry, selecting the colour scheme and the text scheme the pressing insert to add to available rotations.

To add to the rotations in use, select a rotation from left-hand list and press '**Add to rotations in use →**' this rotation should now appear in the right-hand list.

To remove a rotation from the rotations-in-use select a rotation from the right-hand list and press '**← Remove from rotations in use**', this rotation should now appear in the left hand list.

[Screenshot]

To delete a rotation completely, select a rotation from available or in-use and press '**Delete**'.

Rotations-in-use ordering can be changed by dragging a rotation-in-use up and down the rotations-in-use list, clicking on update will save the sequence.

Reset to default available, clears all existing rotations both in-use and available and populates with a default list of rotations,based on licensing.

The rotations-in-use are set to the default rotations on first run, or when the rotations-in-use list is empty, on load of any plan board HL or LL or configure.

All rotation names should follow the text translate system.

Functionality in High Level and Low Level boards should be as before with clicking on rotation button, or selecting drop-down from rotation button or clicking the rotation at on the planning board status bar.

[Screenshot]

These settings will then be reflected on the Planning Boards when the defined Rotation is selected.

[Screenshot]

### Consolidation

*Context: Main Menu > Setup > Configure > Planning › Planning Board Options › Consolidation*

A consolidation criteria can be created and made available system wide.

[Screenshot: Cofigure consolidate]

These can then be seen on the Low Level planning Boards:

[Screenshot: Cofigure consolidate]
