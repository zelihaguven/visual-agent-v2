# Main Menu - Setup - Event Planning - Framework (part 1)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Event Planning > Framework
**Part:** 1 of 2 — sections: Define Events, Production, Events, Nesting, Dependant events, Rename, Report

---

## Define Events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events*

FastReact Event Planning plays a key role in ensuring that the manufacturing or supply is achievable. It does this by calculating when each critical path activity is required and who is responsible for the completion of that activity. Problems in this area are then highlighted by visual warnings on the planning board and though the extensive reporting options. Before any of this can work, however, FastReact must be configured to match the Company's requirements

Two types of event or activity can be controlled; those which relate to individual orders and those that relate to the products. This allows control of the product development stage up to a customer order being placed, and then control of that order right through to the start of production and beyond. This dialog has two separate tabs, dealing separately with Production and Development events. Depending on the configuration of your system only one of these tabs may be visible.

### Production

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Production*

This tab is separated into a number of different pages.

#### Events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Production › Events*

**Enter Event Name:** Enter the name of a new event or select one from the list of existing events. Events have a maximum of 30 alphanumeric characters. Events are sorted alphabetically so it is preferable to name each event carefully to ensure it is sequenced as you want. The easiest way to do this is to start each section with a number.

For example, 010 Event 1, 020 Event 2 and so on. Keep the numeric part the same length to ensure correct sorting. In the example the numeric part is always 3 characters long.

It is good practice to leave a gap of 10 between each event to allow insertions at a later date if necessary.

Ensure that ALL required events are included even if all events are not required on every order. This is the master framework from which events will be selected. If an event is not included here it will not be available for later use.

**Offset time:** Define the default number of working days, before or after, the 'Relative to' point that this event takes place. FastReact uses this offset to calculate the target dates for events. For an example see here (see: Reference > General > Offsets).

**Process time:** Enter the amount of time in minutes that it takes to complete this event. This will then give a load on the person responsible for that event.

**Duration:** It is possible to define the time taken (days) for the event, this in turn is reflected in the Critical Path. For an example see here (see: Reference > General > Durations).

> **Note:** This functionality might be used in conjunction or separately from the Offset value, however we strongly recommend that Durations and Offsets are not applied on the same event.

**Priority:** This function allows the User to create 'Executive Diaries' that are essentially 'To Do Lists'. Events can be prioritised up to a maximum 255. These numbers of priority, 0 to 255, are arbitrary numbers that are assigned to the Event upon creation. The higher the number the greater priority that is placed on the Event.

For reporting purposes the Reporting Tool uses the O.Event_Priority and O.Events_Priority fields in relation to the order and P.Event_Priority and P.Events_Priority fields in relation to the product. The resulting reports can be sorted via either the date field or the above Priority fields.

**Relative to:** This list details the points that each event can be linked to within the production process. The following link points are available:

Order event base date

By default this date will be populated with the date that the Order is created, however you can change this date at any time. The Order base date remains as a fixed date regardless of the planned date of the Order. Defining a Section is not relevant for this link point.

**Order event base date:** This is the date defined on the Orders - Events tab. If this is selected then the Critical Path calculation will be based on this date for the selected Event.

**Release date:** This is the date that a 'package' of materials and information would be released to a production facility. It is based on the preparation start date (below) for the earliest strip in the first section, and works back though the transport allowances to find out when the 'package' needs to be released. If the order is not planned then the release date is calculated from the earliest order delivery date, less any production time allowed for the order (or a default if the latter is zero). The release location may be defined on an order by order basis in the 'Originate from' field.

**Preparation start:** This is the date of the first defined operation for each Section. A Section must also be defined when this link point is selected.

**Load into production:** This is the date that the first items are fed into the planned operation for a Section. It is the start date of the strip on the planning board less any manufacturing throughput time associated with that planning board Row or Group. A Section must also be defined when this link point is selected.

**Change machine:** This is the date for any machine change required before an Order can be started on a planning resource.

For example, it may take a day to change a weaving machine from one pattern to another.

An event such as 'Change machine' could be linked to this point for the engineering departments benefit. A Section must also be defined when this link point is selected.

**Production start date:** This is the date of the start of the strip on the planning board Section. A Section must also be defined when this link point is selected.

**Production end date:** This is the date of the end of the strip on the planning board Section. A Section must also be defined when this link point is selected.

**First complete in section:** This is the date when the first items will complete out of the section It is the start date of the strip on the planning board plus any post manufacturing throughput times that take place in the specified Section (e.g. PACKING and EXAMINATION may take place after SEWINIG). A Section must also be defined when this link point is selected.

**Last complete in section:** This is the date when the last items will complete out of the section. It is the end date of the strip on the planning board plus any post manufacturing throughput times (e.g. PACKING and EXAMINATION may take place after SEWINIG). A Section must also be defined when this link point is selected.

**First despatch from factory:** This is the date when the first items will be dispatched from the Section. It is the first complete date plus any waiting days until transport is available.

For example, production may be complete on Tuesday but the ship does not sail until Friday.

A Section must also be defined when this link point is selected.

**Last despatch from factory:** This is the date when the last items will be dispatched from the Section. It is the last complete date plus any waiting days until transport is available.

For example, production may be complete on Tuesday but the ship does not sail until Friday.

 A Section must also be defined when this link point is selected.

**First available to next section:** This is the date that the first items are available to the next planning Section or to a Customer's DC. Typically this is after transport from the first section to the second section. A Section must also be defined when this link point is selected.

**Last available to next section:** This is the date that the last items are available to the next planning Section or to a Customer's DC. Typically this is after transport from the first section to the second section. A Section must also be defined when this link point is selected.

**First complete in warehouse (DC):** This is the date that the first goods are received into the warehouse or Distribution Centre. This is after transport from the final planned Section. Defining a Section is not relevant for this link point.

**Last complete in warehouse (DC):** This is the date that the last goods are received into the warehouse or DC. This is after transport from the final planned Section. Defining a Section is not relevant for this link point.

**First arrive at customer:** This is the date that the items will first become available to the customer. All post transport operations that occur in the warehouse plus any transport from warehouse to final customer delivery location are considered (in this case the warehouse would normally be termed a distribution centre DC). Defining a Section is not relevant for this link point.

**Last arrive at customer:** This is the date that the last items will become available to the customer. All post transport operations that occur in the warehouse plus any transport from warehouse to final customer delivery location are considered (in this case the warehouse would normally be termed a distribution centre DC). Defining a Section is not relevant for this link point.

**First order delivery date:** This is the first contracted delivery date on the Order. Defining a Section is not relevant for this link point.

**Last order delivery date:** This is the last contracted delivery date on the Order. Defining a Section is not relevant for this link point.

**Another event:** An event can be linked to another event in such a way that event 1 must be completed before event 2 can begin.

**Section:** Select the Section to which the chosen event is to be linked.

For example, the event, 'Fabric in-house', may be linked to the Section 'CUTTING' whereas, 'Threads in-house' may be linked to the Section 'SEWING'.

In systems which have multiple sections select < Earliest section > or < Final section > in which case the section actually linked can vary according to the order and which operations are valid on that order. In the example above, work may not flow through Cutting so linking all events to cutting would not work as the link point would be missing on some orders. However linking to < Earliest section > would allow FastReact to work around cutting for some orders and sewing for others.

**User normally responsible:** Select the user who will be most likely to take responsibility of each event. This is just a default setting for the event and the user responsible can be over-ridden at the Timetable and/or Customer level.

**or anyone in this users department:** Used in conjunction with the above option, this option allows anyone that is part of the above selected users department to update the selected event.

**Allow update by group:** Normally events can only be updated by the person responsible for that event (or that person’s proxy). A user group can also be selected whose members will also be able to update the event.

**Status colour:** This is the colour of the event name.

**Colour (button):** This button enables the user to select the colour of the event name. This will be seen on the Critical Path board and the High Level boards.

**Linked updates:** This option, when enabled, allows the user to update a number of orders at once, based on the link option that you specify here.

> **Note:** Different linking mechanisms can be specified for each event, giving greater flexibility.

The options currently available are as follows:

**None:** The link option is disabled.

**Base code:** The link will be the Order base code. This is the whole order reference or that part of the order reference which is before the double colon separator.

For example, order reference 123::blue and 123::red will match.

**Customers:** All orders which have the same customer as the updated order.

**Order set:** All orders that belong to the same Order Set as the updated order.

**Products:** All orders that have the same Product as the updated order.

**Update when work passes:** The event may, optionally, be linked to a specific production operation so that when work is first logged against this operation the event is updated as having been completed on that date.

**Link to material group:** Check this option if it is required to be able to display and report those items on the Bill of Materials that is attached to each order. FastReact will allow the user to report material dates based on the target date for events. It will also show this in Event displays immediately following the event to which they are attached.

This option must be enabled in Main Menu - Setup - Configure - Event planning.

**Warn if event conflicts with:** This option allows the user to setup two events so that if the highlighted event is Earlier or Later than the selected event, FastReact will give a visual warning on the Critical Path board. One event name will be Red and one Orange in this case.

**Not earlier:** The selected event will produce a warning if it is Earlier than the highlighted event.

**Not later:** The selected event will produce a warning if it is Later than the highlighted event.

**External reference:** This is used for indexing when importing data into FastReact. Enter a unique number, across both Production and Development events, to associate with this Event. FastReact will raise an error if the number is not unique. This allows the event to be renamed whilst retaining integrity in the import file.

**Collaboration id:** When Collaboration has been enabled on the system, this option will appear. The events that will be collaborated between the Host and the Remote systems will have the same id here.

##### Options

**Event is active:** If enabled then FastReact will automatically mark the event as active in the Timetable set-up. This can be over-ridden on each individual Timetable and is just a default setting.

**Event uses production calendar:** Allow events to optionally use the production calendar from the planning board row or group that the order is loaded on. If there are multiple strips then it will use the calendar from the last strip it finds. If the strips are not planned it will use the normal Critical Path calendar.

**Event is critical to production start:** If enabled then FastReact will automatically mark the event as critical in the Timetable set-up. This can be over-ridden on each individual Timetable and is just a default setting.

**Event is used as a reminder only:** If enabled then FastReact will automatically mark the event as a reminder event in the Timetable set-up. This can be over-ridden on each individual Timetable and is just a default setting.

**Event is always reported:** This allows a report to be filtered on Late events only but still include specific events, whether late or not. The value returned from the report generator for each event will be 0 if the event is not selected here and it is not late. If it is late or it is selected here then the value will be 1.

**Event complete date not exported:** The complete date for this event is never exported. This allows an export to another system, where Event planning is shared with FastReact, and this would avoid completion dates in FastReact overwriting completion dates in the other system. The Event must be reported using the report field O.EVENT_DONE_X.

**Event is "nominated" as special:** You may select one event as a special event, this will allow you to view an additional rotation of the planning board by pressing the F3 key. Any strips that get coloured green means that the nominated event has been completed on that order.

**Update event only when operation is complete:** This option will only allow the completion of an event when the operation has been completed.

**Target date for event is based on preceding completion date:** This option will reset the event target date for the event based upon the completion date of the event before. This means that if the preceding event is finished two days early, then the events target date will be driven by the completion date of the preceding event.

**Delegate Complete/Skipped/Offset update to collaborative partner:** When Collaboration is enabled, and the event will be one of the collaborated events, the user can assign responsibility for these dates on that event to the collaborative partner.

**Delegate Expected update to collaborative partner:** When Collaboration is enabled, and the event will be one of the collaborated events, the user can assign responsibility for this date on that event to the collaborative partner.

**Delegate target update to collaborative partner:** When Collaboration is enabled, and the event will be one of the collaborated events, the user can assign responsibility f this date on that event to the collaborative partner.

#### Nesting

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Production › Nesting*

This is a licence option and will not be visible if Dependant Events are selected in the licence file.

This applies equally well to production and development events.

This dialog allows you to create Parent and Child events. Child events would normally be considered as belonging to a Parent Event. By using Parent and Child events the amount of detail viewed by a user can be tailored to their needs.

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

**Nesting lists:** Drag events from the list on the right of this dialog. To create a Parent event drop the dragged even into a blank space below the last event. To create a Child event drop the event on a Parent event.

Events may be dragged back to the right hand list so that they no longer participate in the Parent/Child relationship.

#### Dependant events

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Production › Dependant events*

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

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Production › Rename*

Events may be renamed at any time.

**Select event:** This is a list of all the events that have been created within the FastReact system.

**Enter a new name:** Once the event that has to be renamed has been selected, the new event name can be entered here.

**Rename (button):** This button will rename the event.

#### Report

*Context: Main Menu > Setup > Event Planning > Framework › Define Events › Production › Report*

This provides a simple check list of the event framework and this list may be printed.
