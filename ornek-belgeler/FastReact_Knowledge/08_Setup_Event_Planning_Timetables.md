# Main Menu - Setup - Event Planning - Timetables

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Event Planning > Timetables
**Index keywords:** Event Planning, Timetables

---

## Timetables

*Context: Main Menu > Setup > Event Planning > Timetables › Timetables*

FastReact makes use of Timetables to define events for different customers, different products etc. Timetables are used to define an individual list of events (including date offsets and responsibilities) that need to take place before production of an Order can commence. Any number of Timetables can be configured. These are then attached to Orders or Products. Each Timetable consists of a list of events, the executive responsible for that event and an offset which is used by FastReact to calculate when the event should (in an ideal world) take place - the event target date.

The dialog is split into a number of tabs, the first is used to create timetables, the second to configure these whilst the third allows you to rename a timetable.

### Define

*Context: Main Menu > Setup > Event Planning > Timetables › Timetables › Define*

**Timetable name:** Enter a new timetable name or select an existing one from the list. Timetable names may be up to 15 characters long.

**Production timetable / Development timetable / Range design timetable:** Specify whether a newly entered Timetable is to be used for Production (Order related) events or for Development (Product related) events.

> **Note:** Once a Timetable has been created you cannot alter this attribute.

**Description:** Enter a description of the timetable up to 50 characters long.

**Calendar:** Select a calendar from the list. This will be used to calculate the Target date for each event by taking account of any holidays and weekends.

> **Tip:** If you would like FastReact to work in calendar days rather than working days you could create a calendar with no weekends or holidays and use this for your Timetable.

##### Options

**Default timetable:** One timetable can be specified to act as the default for new products or orders.

#### Events

*Context: Main Menu > Setup > Event Planning > Timetables › Timetables › Define › Events*

By default all Timetables will take their settings from the Event Framework. This dialog enables you to tailor events for each Timetable.

**Select a timetable:** Select a Timetable to amend.

**Print (button):** This button will print the selected Timetable and its events.

##### Event matrix

This is where details for the selected Timetable can be specified. The columns are:

**Event:** This is a list of the events that have been created in the Framework. The user cannot add or amend this list from within a timetable, only from the Framework.

**Relative to:** This is the link point from which the target date will be calculated using the specified offset. This link point is specified under Framework and cannot be altered for an individual Timetable.

**User:** Select the user that is responsible for each individual event for the selected Timetable. In this way different users can be responsible for the same event in different timetables.

**Offset:** The offset is used by FastReact to calculate when an event should happen using the Timetable calendar. Offsets should be entered as a negative number, the number of working days before the 'Relative to' link point, or positive if the event must happen after the link point.

**Duration:** This is the duration of the event.

**Options:** This consists of four columns of coloured selection boxes. Each column enables a different feature or attribute for the event. Attributes can be toggled by clicking a box with the mouse. A box will be grey if it is turned off. The columns are:

[Screenshot: Event Key]

**Required (Green):** If selected FastReact will consider these events as required, however certain events may be required only under unusual circumstances. These events must be created in the Event Framework but can be turned off for specific timetables.

**Skipped (White):** Events that are not required (above) will not appear for any order or product using this timetable. Skipped events are similar but Skipped events can be 'un Skipped' on an Order by Order basis. This allows you to have events which may or may not be required on individual orders. The same result could be achieved by having different timetables with different events marked as required or not required, but this method is more flexible.

**Reminder (Yellow):** These events will be given target dates as with all other events. However, as soon as these events become due (or overdue) FastReact will consider them to be complete. This will give the executive responsible more warning and hence less chance of overlooking the event.

**Critical (Orange):** The user can flag events as critical, these are events that MUST NOT be missed. Many events can be caught up later but some just cannot. If the materials miss the boat to the factory then production will not be able to start, whereas if the quality has not been approved then a start can be made, albeit with some risk attached. If a critical target date is missed then FastReact will identify this problem visually on the planning board.

Another function of critical event dates is that even when completed they will still play a part in the calculation of earliest possible start date whereas normal events do not.

### Rename

*Context: Main Menu > Setup > Event Planning > Timetables › Timetables › Rename*

You can rename a timetable at any time.

**Select a timetable to rename:** This is a list of all the timetables that have been created within the FastReact system.

**Enter a new name:** Once the timetable that has to be renamed has been selected, the new timetable name can be entered here.

**Rename (button):** This button will rename the timetable.

#### Copy

*Context: Main Menu > Setup > Event Planning > Timetables › Timetables › Rename › Copy*

**Select a timetable to copy:** This is a list of all the timetables that have been created within the FastReact system.

**Enter a new name:** Once the timetable that has to be copied has been selected, the new timetable name can be entered here.

**Rename (button):** This button will copy the timetable.
