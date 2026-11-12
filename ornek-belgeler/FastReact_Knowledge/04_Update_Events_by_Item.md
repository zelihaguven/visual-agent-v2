# Main Menu - Update - Events by Item

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Update > Events by Item
**Index keywords:** Events

---

## Update events

*Context: Main Menu > Update > Events by Item › Update events*

This dialog has two tabs, one for Production (order based) events and the other for Development (product based) events. Both tabs are essentially the same in format and operation so the description below will apply to both. Where there are differences these will be highlighted

### Product events / Development events

*Context: Main Menu > Update > Events by Item › Update events › Product events / Development events*

**Select an order/product to update:** Select the order or product that requires updating. The events relevant to the selection appear in the table below.

Timetable

This is the pre-defined Timetable and will appear automatically upon selection of the order.

**Start, Completed and Expected Dates.:** These dates default to the system date of the PC on which FastReact is running.

- The start date will only be visible if the option is enabled on the Event Planning setup dialog. This date denotes the date on which the event was started.
- The completed date denoted the date that the event was completed.
- The expected date denotes the date that the planner expects the event to be completed.

**Skip:** Events which have been skipped on for an order or product will be hidden when this dialog is viewed, checking this box will make those events visible.

#### Update table

*Context: Main Menu > Update > Events by Item › Update events › Product events / Development events › Update table*

**Note:** Notes relating to a certain event can be added from this dialog. Click in the Note column next to the event to which the note relates to and the normal notes dialog will appear.

The notebook icon will appear blue next to any events with a note attached to it.

**Event:** This column shows all the events that are associated with the selected item (order/product).

The '^' symbol shows the users that the events are sorted by the Event column. This can be toggled between the Regd (Required) complete column.

**Reqd complete:** This column shows the required complete date that FastReact has calculated for each event. This will be the date that staff should strive to meet as any slippage beyond this date would endanger the start of production.

The '^' symbol shows the users that the events are sorted by the Reqd complete column. This can be toggled between the Event column.

**Started:** This date is enabled via the Setup – Configure – Event Planning, Allow update of event start dates.

With this enabled, event start dates can be altered and change to suit the planner.

**Completed:** This is the date that the event was completed or a '-' if not complete. Entering or clearing a date is performed by clicking in this column next to the relevant event. The date will be taken from the date selection at the top of this column.

**Expected:** This is the date that the event is expected. You can enter of clear a date by clicking in this column for the relevant event. The date will be taken from the date selection at the top of this column.

**Offset / Duration:** The normal offset defined in the timetable attached to the selected item can be altered in order to delay or pull forward the target dates for events. A new offset can be typed in, or the calendar can be accessed via right clicking in this column and selecting the required date the resulting calendar that FastReact will display, then click the Calculate button. FastReact will calculate the offset based on the current target date and the date you entered and put the resulting offset back into the selected column.

By clicking on the offset header the column will switch to the Duration view. The normal durations defined on the timetable attached to the selected item can be altered in order to delay or pull forward the target dates for events. The new duration can be typed in manually.

> **Note:** There is a difference between changing the offset and entering an expected date. With a fixed expected date any variance values (is the event late or not) will be calculated as the difference between the target and expected dates. Re-planning the order or changing the product launch date will have will not effect the target date. However, if you change the offset you will change the target date, but the target date will still be linked to the planning board or product launch date. If you change these the target dates will change accordingly.

**Skip:** Events may be skipped on for an order or product. Skipped events will not be reported or take any role in calculations. Skipped events can be unskipped at any time.

#### Security

*Context: Main Menu > Update > Events by Item › Update events › Product events / Development events › Security*

FastReact maintains tight security on who can do what. Events can be linked to a specific person (and/or their deputy) and only that person can change any data for that event. This security is defined within the Event framework, but can be overridden on specific timetables, and finally for specific customers. Events that you cannot update are shown in purple.

#### Parent and Child events

*Context: Main Menu > Update > Events by Item › Update events › Product events / Development events › Parent and Child events*

Events may be 'nested' so that there are 'Parent and Child' events. Parent events are shown in bold. If all Child events that belong to a Parent event have been completed then FastReact will consider the Parent event to be complete as well. Similarly if any Child event is incomplete then FastReact will consider the relevant Parent event to be incomplete as well.

If a Parent event is updated then FastReact will mark all Child events, relating to that Parent event, as complete. Direct uncompletion of a Parent event cannot be done as its status is entirely dependant upon its Child events. In other words, the Child event(s) have to be uncompleted first.

**Multi Update (button):** An order may belong to a Set. If so then FastReact allow the updating of all linked events (as defined on the Framework and Orders dialogs).

**Select:** With this option enabled, before updating FastReact will display all the orders that are part of the Set and as such will have their linked events updated. The resulting dialog will allow the de-selecting of the entire Set or individual orders within the Set.

**Update Order (button):** This button will update the changes made against the selected order.

#### Late Event Updates.

*Context: Main Menu > Update > Events by Item › Update events › Product events / Development events › Late Event Updates.*

Once the requisite number of Late Reasons have been turned on in the Licence and the option to Require selection of a reason when updating late events has been selected, then any time that the user clicks on a strip on the Planning Board and selects Events Reports - Update, and the particular event that the user is updating is late, then the Late Event Update dialog box will automatically appear. This will force the user to select, from a list, a reason as to why the event is late. Until a reason has been selected, the dialog will remain on screen.

> **Note:** Late Event Updates cannot be accessed via either:

- Update – Event by Event
- Update – Multiple Updates
