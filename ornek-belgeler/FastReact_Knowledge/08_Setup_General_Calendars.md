# Main Menu - Setup - General - Calendars

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > General > Calendars
**Index keywords:** Calendar

---

## Calendars

*Context: Main Menu > Setup > General > Calendars › Calendars*

To be able to use FastReact at least one Calendar must created. When calculating target dates and production times FastReact will use these calendars to give realistic available dates and production of times. Calendars may be attached to row or group on the planning board(s) to give each a specific working pattern (holidays, weekends) and capacity (hours worked per day) Calendars are also used in critical path planning to calculate event target dates.

The same calendar can be attached to several different objects in FastReact.

For example a production calendar for planning rows can also be used as an event calendar. However, any alterations you make to a calendar (e.g. overtime, working at a weekend or holiday) will affect anything using this calendar.

Exceptions to a calendar (i.e. anything that is different to the defined standard week such as a holiday or overtime hours) cover a period of 4 years (12 months before the start of the current week to 36 months into the future). At the start of each week the oldest week in the calendar is dropped and a new week added. The new week is automatically filled with the normal working hours per day as defined for the default week. It is therefore necessary to review and amend calendars (for new holidays etc.) at least once per year.

> **Note:** FastReact uses the workstation clock to determine the current date. It is important that this date is correct to avoid calendar inconsistencies. In a network environment it is essential that all computers have the same date setting, this should be imposed by the network at log on to prevent users tampering with their clock.

### Define

*Context: Main Menu > Setup > General > Calendars › Calendars › Define*

The daily working hours entered under this dialog can be amended from this default from within the planning board.

For example, to add overtime.

**Calendar name:** Enter a new calendar name or select one from the list. Calendars names can be up to 15 characters long.

**Update/Insert (button):** This button will update a current calendar or insert a new one.

**Delete (button):** This button will delete the selected calendar.

#### Working hours

*Context: Main Menu > Setup > General > Calendars › Calendars › Define › Working hours*

This tab allows the user to set the start time (range midnight to noon) and the normal working hours (0 to 24:00 hours) for each day. The working hours should be the actual production hours in the day.

For example, typically these exclude unpaid breaks such as lunch but include paid breaks).

This is a default working pattern for each week.

**Start time:** This is the normal start time for the first shift.

**Work hours:** This is the combined total working hours for all shifts.

**Total hours split into shifts:** This is how many shifts the working day is split into.

#### Breaks tab

*Context: Main Menu > Setup > General > Calendars › Calendars › Define › Breaks tab*

This tab allows the user to set daily breaks. It is only necessary to configure breaks if the exact time of day is required in your production planning.

For example, 3 production hours from 8:00 am is actually 11:20 am, as there is a 20 minute break between 10:00 am and 10:20 am).

**Week day buttons:** The buttons across the top of this page allow you to select which day of the week you want to define.

**Week day copy buttons:** Using the Copy buttons down the side of the page you can copy the current breaks pattern to other days of the week.

##### Breaks

Four breaks can be set per shift. Each shift MUST be the same length.

**Start time:** Enter the start time of the break for the shift.

**Duration:** Enter the duration of the break.

**Shift toggle (button):** - [Icon: Left Right Move] Toggle shift.

This button will, if the system has multiple shifts, switch between these shift breaks. There is a number next to the button indicating which shift is currently visible.

##### Overtime

Four overtime breaks can be set per shift.

**Overtime trigger:** This number will normally be the total working hours per day. Once this figure has been exceeded then the overtime breaks will initiate.

###### Use these breaks if working overtime

**Start time:** Enter the start time of the break for the shift if the overtime trigger has been triggered.

**Duration:** Enter the duration of the break if the overtime trigger has been triggered.

### Rename

*Context: Main Menu > Setup > General > Calendars › Calendars › Rename*

Renaming of an order can take place at any time.

**Select a calendar:** This is a list of existing Calendars. Select the Calendar you want to copy from the incremental search list.

**Enter a new name:** Enter a new calendar name here. FastReact will validate the new calendar and only allow a rename to be made if the new calendar reference does not already exist.

**Rename (button):** This button will rename the selected calendar.

**Copy (button):** This button will copy the selected calendar.

### Holidays

*Context: Main Menu > Setup > General > Calendars › Calendars › Holidays*

This tab allows the user to enter holidays and amend standard working hours.

**Select a calendar:** Select the required calendar to amend from this list.

## Calendar

*Context: Main Menu > Setup > General > Calendars › Calendar*

This table shows the working hours for any week on the selected calendar. The days are colour coded as shown below the table to identify days where the working hours are different to normal.

###### Colour coding

- [Icon: Holiday key] Colour Key.

##### Working hours

The working hours for any day of the selected week can be seen on this dialog.

**Reset (button):** - [Icon: Delete] Reset working hours.

This button resets the working hours to zero for the selected day.

Default

- [Icon: Hol clear] Toggle shift.

This button will restore the default hours for the selected day.

**Update (button):** This button will update the holidays on the selected calendar.

**Show today (button):** Press this button to highlight today’s date within the calendar.

### Report

*Context: Main Menu > Setup > General > Calendars › Calendar › Report*

This allows the user to display and print the working hours defined on your calendars.

**Select a calendar:** Select the required calendar.

##### Calendar

This dialog displays the calendar.

**Print (button):** This button will print the currently selected calendar.

### Special calendars

*Context: Main Menu > Setup > General > Calendars › Calendar › Special calendars*

FastReact allows the user to define 2 special calendars with up to 24 periods in each. These are used for specifying financial periods for reporting and other special periods such as seasons.
