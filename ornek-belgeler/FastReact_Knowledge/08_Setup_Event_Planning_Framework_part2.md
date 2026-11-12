# Main Menu - Setup - Event Planning - Framework (part 2)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Event Planning > Framework
**Part:** 2 of 2 — sections: Development, Events, Nesting, Dependant events, Rename, Report, Designs, Events

---

### Development

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development*

#### Events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development › Events*

**Enter Event Name:** Enter the name of a new event or select one from the list of existing events. Events may be up to 30 characters long. Events are be sorted alphabetically so it is preferable to name each event carefully to ensure it is sequenced as you want. The easiest way to do this is to start each section with a number.

For example, 010 Event 1, 020 Event 2 and so on. Keep the numeric part the same length to ensure correct sorting. In the example the numeric part is always 3 characters long.

It is good practice to leave a gap of 10 between each event to allow insertions at a later date if necessary.

ALL required events should be included even if all events are not required on every order. This is the Parent framework from which events will be selected. If an event is not included here it will not be available for later use.

**Offset time:** Define the default number of working days, before or after, the 'Relative to' point that this event takes place. FastReact uses this offset to calculate the target dates for events

**Process time:** Enter the amount of time in minutes that it takes to complete this event. This will then give a load on the person responsible for that event.

**Duration:** This is the time normally taken to complete the event, in days.

**Priority:** This function allows the User to create 'Executive Diaries' that are essentially 'To Do Lists'. Events can be prioritised up to a maximum 255. These numbers of priority, 0 to 255, are arbitrary numbers that are assigned to the Event upon creation. The higher the number the greater priority that is placed on the Event.

For reporting purposes the Reporting Tool uses the O.Event_Priority and O.Events_Priority fields in relation to the order and P.Event_Priority and P.Events_Priority fields in relation to the product. The resulting reports can be sorted via either the date field or the above Priority fields.

**Relative to:** This list details the points that each event can be linked to within the production process. The following link points are available:

**Launch date:** This is the date as proscribed in the Product launch date.

**Another Event:** Allows the event to be linked to a calendar date derived from a relationship with another event

For example, one event date is dependent on another, rather than a point in the strip.

**User normally responsible:** Select the user who will be most likely to take responsibility of each event. This is purely a default setting for the event and the user responsible can be over-ridden at the Timetable and/or Customer level.

**Also allow update by group:** Select the user group that can also update this event. This is used so that anyone in merchandising can update the same events as another user who is in the merchandising user group even though they are not the normal user for the event.

###### Status colour

This is the colour of the event name.

**Colour (button):** This button enables the user to select the colour of the event name. This will be seen on the Critical Path board and the High Level boards.

**Warn if event conflicts with:** This option allows the user to setup two events so that if the highlighted event is Earlier or Later than the selected event, FastReact will give a visual warning on the Critical Path board. One event name will be Red and one Orange in this case.

**Not earlier:** The selected event will produce a warning if it is Earlier than the highlighted event.

**Not later:** The selected event will produce a warning if it is Later than the highlighted event.

**External reference:** This is used for indexing when importing data into FastReact. Enter a unique number, across both Production and Development events, to associate with this Event. FastReact will raise an error if the number is not unique. This allows the event to be renamed whilst retaining integrity in the import file.

**Collaboration id:** When Collaboration has been enabled on the system, this option will appear. The events that will be collaborated between the Host and the Remote systems will have the same id here.

##### Options

**Event is used as a reminder only:** If enabled then FastReact will automatically mark the event as a reminder event in the Timetable set-up. This can be over-ridden on each individual Timetable and is just a default setting.

**Target date for event is based on preceding completion date:** This option will reset the event target date for the event based upon the completion date of the event before. This means that if the preceding event is finished two days early, then the events target date will be driven by the completion date of the preceding event.

**Delegate Complete/Skipped/Offset update to collaborative partner:** When Collaboration is enabled, and the event will be one of the collaborated events, the user can assign responsibility for these dates on that event to the collaborative partner.

**Delegate Expected update to collaborative partner:** When Collaboration is enabled, and the event will be one of the collaborated events, the user can assign responsibility for this date on that event to the collaborative partner.

**Delegate target update to collaborative partner:** When Collaboration is enabled, and the event will be one of the collaborated events, the user can assign responsibility f this date on that event to the collaborative partner.

#### Nesting

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development › Nesting*

This is a licence option and will not be visible in Dependant Events are selected in the licence file.

This applies equally well to production and development events.

This page allows you to create Parent and Child events. Child events would normally be considered as belonging to a Parent Event. By using Parent and Child events the amount of detail viewed by a user can be tailored to their needs.

For example, a Merchandiser might need to be aware of all events whereas the Planner may only need to know that the Parent Event is complete/outstanding and would not be interested in the detail.

Child events can be hidden in on screen and hard copy reports as applicable. A Parent Event is automatically completed by FastReact if all of its Child events are completed. Equally any uncompleted Child Events will automatically be completed should a Parent Event be completed manually.

Example:-

| Parent | Child |
|---|---|
| Lab Dip Approval | Lab Dip Submit |
| | Shade Approval |
| | Fade test approval |
| | Wash test approval |
| | Water resistance |

**Nesting lists:** Drag events from the list on the right of this dialog. To create a Parent event drop the dragged even into a blank space below the last event. To create a Child event drop the event on a Parent event

Events may be dragged back to the right hand list so that they no longer participate in the Parent/Child relationship.

#### Dependant events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development › Dependant events*

This is a licensed option and will not be visible if Nested events are enabled.

##### Select a target event

This is a list of all the Production events.

###### Selected target event

The selected target event is an event from the above list which MUST have a link to the root event

##### Target event depends on these

This is a list of events upon which the target event is dependant. A target event can have a maximum of five dependant events.

###### Fixed date event (root event)

This is the top level event (root) which has a fixed date.

###### Is linked to

This field will detail what the root event is linked to.

##### Drag to central list

On this list will appear ONLY the events which have the Relative to field marked as Another event.

**Save (button):** This button will save the dependant event framework.

#### Rename

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development › Rename*

Events may be renamed at any time.

**Select an event to rename:** This is a list of all the events that have been created within the FastReact system.

**Enter a new name:** Once the event that has to be renamed has been selected, the new event name can be entered here.

**Rename (button):** This button will rename the event.

#### Report

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development › Report*

This provides a simple check list of your event framework and this list may be printed.

#### Designs

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Development › Designs*

### Events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Events*

**Enter Event Name:** Enter the name of a new event or select one from the list of existing events. Events may be up to 30 characters long. Events are be sorted alphabetically so it is preferable to name each event carefully to ensure it is sequenced as you want. The easiest way to do this is to start each section with a number.

For example, 010 Event 1, 020 Event 2 and so on. Keep the numeric part the same length to ensure correct sorting. In the example the numeric part is always 3 characters long.

It is good practice to leave a gap of 10 between each event to allow insertions at a later date if necessary.

ALL required events should be included even if all events are not required on every order. This is the Parent framework from which events will be selected. If an event is not included here it will not be available for later use.

**Offset time:** Define the default number of working days, before or after, the 'Relative to' point that this event takes place. FastReact uses this offset to calculate the target dates for events

**Process time:** Enter the amount of time in minutes that it takes to complete this event. This will then give a load on the person responsible for that event.

**Duration:** This is the time normally taken to complete the event, in days.

**Priority:** This function allows the User to create 'Executive Diaries' that are essentially 'To Do Lists'. Events can be prioritised up to a maximum 255. These numbers of priority, 0 to 255, are arbitrary numbers that are assigned to the Event upon creation. The higher the number the greater priority that is placed on the Event.

For reporting purposes the Reporting Tool uses the O.Event_Priority and O.Events_Priority fields in relation to the order and P.Event_Priority and P.Events_Priority fields in relation to the product. The resulting reports can be sorted via either the date field or the above Priority fields.

**Relative to:** This list details the points that each event can be linked to within the production process. The following link points are available:

Range end date

This is the end date of the Range as proscribed in the Range Planning.

Range start date

This is the start date of the Range as proscribed in the Range Planning.

Another Event

Allows the event to be linked to a calendar date derived from a relationship with another event

For example, one event date is dependent on another, rather than a point in the strip.

**User normally responsible:** Select the user who will be most likely to take responsibility of each event. This is purely a default setting for the event and the user responsible can be over-ridden at the Timetable and/or Customer level.

**Also allow update by group:** Select the user group that can also update this event. This is used so that anyone in merchandising can update the same events as another user who is in the merchandising user group even though they are not the normal user for the event.

###### Status colour

This is the colour of the event name.

**Colour (button):** This button enables the user to select the colour of the event name. This will be seen on the Critical Path board and the High Level boards.

##### Options

**Target date for event is based on preceding completion date:** This option will reset the event target date for the event based upon the completion date of the event before. This means that if the preceding event is finished two days early, then the events target date will be driven by the completion date of the preceding event.

#### Nesting

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Events › Nesting*

This is a licence option and will not be visible if Dependant Events are selected in the licence file.

This applies equally well to production and development events.

This page allows you to create Parent and Child events. Child events would normally be considered as belonging to a Parent Event. By using Parent and Child events the amount of detail viewed by a user can be tailored to their needs.

For example, a Merchandiser might need to be aware of all events whereas the Planner may only need to know that the Parent Event is complete/outstanding and would not be interested in the detail.

Child events can be hidden in on screen and hard copy reports as applicable. A Parent Event is automatically completed by FastReact if all of its Child events are completed. Equally any uncompleted Child Events will automatically be completed should a Parent Event be completed manually.

Example:-

| Parent | Child |
|---|---|
| Lab Dip Approval | Lab Dip Submit |
| | Shade Approval |
| | Fade test approval |
| | Wash test approval |
| | Water resistance |

**Nesting lists:** Drag events from the list on the right of this dialog. To create a Parent event drop the dragged even into a blank space below the last event. To create a Child event drop the event on a Parent event

Events may be dragged back to the right hand list so that they no longer participate in the Parent/Child relationship.

#### Dependant events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Events › Dependant events*

This is a licensed option and will not be visible if Nested events are enabled.

##### Select a target event

This is a list of all the Production events.

###### Selected target event

The selected target event is an event from the above list which MUST have a link to the root event

##### Target event depends on these

This is a list of events upon which the target event is dependant. A target event can have a maximum of five dependant events.

###### Fixed date event (root event)

This is the top level event (root) which has a fixed date.

###### Is linked to

This field will detail what the root event is linked to.

##### Drag to central list

On this list will appear ONLY the events which have the Relative to field marked as Another event.

**Save (button):** This button will save the dependant event framework.

#### Rename

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Events › Rename*

Events may be renamed at any time.

**Select an event to rename:** This is a list of all the events that have been created within the FastReact system.

**Enter a new name:** Once the event that has to be renamed has been selected, the new event name can be entered here.

**Rename (button):** This button will rename the event.

#### Report

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Events › Report*

This provides a simple check list of your event framework and this list may be printed.

### Analysis

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Analysis*

##### Reason for late event completion.

This feature is a Licence option and can be turned on and off via the Event Analysis option on the Licence option screen. Once the Licence option has been selected and FastReact started a new tab will appear in the Setup - Event Planning - Framework menus. The option is called Late Analysis.

During the Set up phase of the FastReact system the User, when choosing to use Late Analysis, will be given a dialog box with 25 reason descriptions numbered 1 to 25. These fields require the User to select a number and rename it, thereby designating one of the descriptions as that late reason. There are also check boxes next to the descriptions, these check boxes allow for the selecting and de-selecting of valid Late Reasons.

**Enter a new description:** Enter a description for the late reason.

**Rename (button):** Analysis descriptions may be renamed at any time.

> **Note:** Late reasons can be renamed at anytime however, this will not change any Notes that have had this reason applied to the event prior to the rename.

There are two further options available for the User on this screen. These are:

**Require selection of a reason when updating late events:** This forces the user to select a Late Reason for any late event that the user is passing.

**Add failure reason to note events:** This check box places the Late Reason selection that the user has chosen in the Notes section of the Products and Orders. Reports will also be able to be created based upon the Notes.

**Save (button):** This button will save the updated late event completed reasons.

##### Reason for event failures.

This feature is a Licence option and can be turned on and off via the Event Analysis option on the Licence option screen. Once the Licence option has been selected and FastReact started a new tab will appear in the Setup - Event Planning - Framework menus. The option is called Late Analysis.

During the Set up phase of the FastReact system the User, when choosing to use Late Analysis, will be given a dialog box with 25 reason descriptions numbered 1 to 25. These fields require the User to select a number and rename it, thereby designating one of the descriptions as that late reason. There are also check boxes next to the descriptions, these check boxes allow for the selecting and de-selecting of valid Late Reasons.

**Enter a new description:** Enter a description for the late reason.

**Rename (button):** Analysis descriptions may be renamed at any time.

> **Note:** Late reasons can be renamed at anytime however, this will not change any Notes that have had this reason applied to the event prior to the rename.

**Save (button):** This button will save the updated reason for event failures.
