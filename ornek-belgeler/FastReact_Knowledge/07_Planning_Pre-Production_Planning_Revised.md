# Main Menu - Planning - Pre-production - Revised

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > Pre-Production Planning > Revised
**Index keywords:** Revised

---

## Preproduction Plan - Revised

*Context: Main Menu > Planning > Pre-Production Planning > Revised › Preproduction Plan - Revised*

This Planning Board shows the critical path activities driven by the application of a Critical Path Timetable to Orders and Products.

### Planning Board

*Context: Main Menu > Planning > Pre-Production Planning > Revised › Preproduction Plan - Revised › Planning Board*

##### Menu bar

###### Sorting

This can be further re-orientated based on the User selections from the menu bar at the top of the dialog, thus:

- By Order, Event, Due Date
- By Event, Due Date
- By Exec, Due Date
- By Customer, Exec, Event, Due Date
- By Supplier, Order, Event, Due Date

Further refinements based on the following options are possible:

- All events
- All incomplete events
- Late incomplete events
- All complete events

Where there are Dependent Events applied to the Critical Paths in use, it is possible to gain a view of these by right clicking in the board and selecting show Dependencies.

**Sort rotation (button):** - [Icon: Sort rotation] Sort rotation view.

This option allows the user to select the sort order in which the events will be displayed on the Pre-production planning board. The options are:

- By Order, Event, Due date
- By Event, Due date
- By Exec, Due date
- By Exec, Order, Due date
- By Customer, Exec, Event, Due date
- By Supplier, Order, Event, Due date

**Event status (button):** - [Icon: Event status] Event status view.

This option allows the user to select the type of event status to view on the Pre-production planning board. Event status' that can be viewed are:

- All events
- All Incomplete events
- Late Incomplete events
- All Complete events

**Scrolling (button):** - [Icon: Scrolling] Scrolling left and right.

The critical path planning board can be scrolled left and right. The bar in the middle of the icon can also be used to scroll the planning board right and left.

**View all events / View no events (button):** - [Icon: Expand] View all events.
- [Icon: Contract] View no events.

These two buttons allow the user to either view, on the critical path planning board, all the events associated with an order or, hide all the events associated with an order.

**Find function (button):** - [Icon: Find] Find function.

This works in the same way as Find in Low Level or High Level Planning Boards.

**View Reports (button):** - [Icon: report] View reports.

The FastReact Reporting functionality can be accessed from the Critical Path planning board.

**Save (button):** - [Icon: Save report] Save.

This button will save any changes made to the Critical Path planning board.

**Update date (button):** - [Icon: Date] Update date.

This is the Update date of the event.

**Text define (button):** - [Icon: Text define] Text define.

This button will open the Text Define dialog to allow the user to select text field which will be displayed on the Critical Path planning board.

##### Main window

In the main window will be, depending upon the sort setup, a list of Orders, Events, Execs or Customers. This list will have a Critical Path associated with each item on it and if the user drills down on an item then the events become visible. FastReact will show Critical Paths for Orders, and Products.

Each event can have its start date, and if it has a duration, its duration marked on the date scale which runs along the top of the window. These dates and other event information are entered on the main window (below) via the Text Define button. This option allows the user to select the information that has to be displayed. Clicking on the "note book" on the Text Defined dialog will set the selected information as the default settings for all users.

[Screenshot: Preproduction board]

#### Performance

*Context: Main Menu > Planning > Pre-Production Planning > Revised › Preproduction Plan - Revised › Planning Board › Performance*

This tab allows the user to view, for each user, the days late and days in hand by events.

This allows the user to track their performance. For more information please click here (see: Main Menu > Planning > Pre-Production Planning > Performance).

#### Loading

*Context: Main Menu > Planning > Pre-Production Planning > Revised › Preproduction Plan - Revised › Planning Board › Loading*

This dialog shows the user a graph of the Loading date against Event count by User and Operation.

For more information please click here (see: Main Menu > Planning > Pre-Production Planning > Loading).

#### Configure

*Context: Main Menu > Planning > Pre-Production Planning > Revised › Preproduction Plan - Revised › Planning Board › Configure*

This tab allows the user to configure the look and make-up of the Pre-production planning board.

##### Show event for

**Orders:** This option will show all events for all Orders only.

**Products:** This option will show all events for all Products only.

**Designs:** This option will show all events for all Designs only.

##### Show process stages

**Do not show:** This option will show the basic event progress.

**Half height:** This option will allow the user to view event, production and transport from the Pre-production planning board.

For example, where the green represents the events, the blue represents the Production (late delivery) and purple represent the Transport.

[Screenshot: HalfHieght]

**Full height:** This is the same as above with the production and transport overlaid on the Pre-production planning board.

For example, where the green represents the events, the blue represents the Production (late delivery) and purple represent the Transport.

[Screenshot: FullHieght]

**Live update:** This option is only available when licenced and allows the user to update events on the CP board via the Live Update dialog.

**Auto save changes when moving to a different item:** This option will force FastReact to save the CP board when the user moves to a different event.

**Hide incomplete events in performance charts:** This option will hide all incomplete events on the Performance charts.

**Use colours to show order status:** This option will colour the Order names their respective Order Status colours as defined during setup.

**Show supply window:** This option will show the Supply window similar to the High Level sourcing view.

**Hide detail rows after a Find:** Under normal circumstances, the result of a Find will show the expanded events view. However with this option selected the results will just be to show the Order after which the user can expand on an Order by Order basis.

**Show materials:** This option will show all required Materials in the expanded event view.

**Only show orders and products where i have events to manage:** This option will only show the Orders and Products that the logged on user has control over.

**Only show events where all parent events are complete:** This option will only show the events that have all their parent events complete.

**Show event notes in a hint window:** This option will display the Event Note, if there are any, when the cursor hovers over the Pre-production strip.

**Show strip extent:** This option will show the strip extent on the Critical Path board.

**Minutes between refresh check for changes:** The user can set the refresh time using this option.

**Update (button):** Update any changes made.
