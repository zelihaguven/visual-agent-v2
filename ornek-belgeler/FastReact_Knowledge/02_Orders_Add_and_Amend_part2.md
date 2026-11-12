# Main Menu - Orders - Add and Amend (part 2)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Orders > Add and Amend
**Part:** 2 of 2 — sections: Events, User values, Property, Forecasting, Hyperlinks, Rename, Copy
**Index keywords:** Extended

---

#### Events

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Events*

This tab shows details of the required events for this order. They are picked up from the timetable which was allocated to the Order, on the General tab.

##### Event table

**Event:** This column lists the events that are required on this order. This is defined within the timetable attached to the order.

**Relative to:** This column shows what each event is relative to.

**Offset / Duration:** This column shows the default offset and or the default duration that has been set up against the specified timetable for that event.

**Fast Track:** If required you can override the default offsets by entering new values. This may be used when an order needs to be 'fast tracked' through the critical path process. Any orders that have fast tracked events will be marked with a purple square the relevant strips on the planning board.

**Skip:** Check this field if you do not want that event to be included for this particular order. If checked FastReact will ignore the event/order.

**Expected:** If an event can only be achieved on a particular date then this date can be entered.

For example, you may know that an event will not be approved until 21st December. Enter this date and the system will use this as target data for the event. When entered FastReact will compare this date with its own calculated date to warn of problems.

**Target (button):** This is the date on which the particular event should be completed by. Clicking on the Retain Event Target Dates button under the Orders menu item will enable FastReact to calculate the target dates.

**Release package originate from:** This location is used to calculate the dates of critical path events that are linked to the 'Release date' To do this FastReact needs to know the transport time for materials and other prerequisites from the source location and the production location (defined by the planning board). This field is only visible when one of the events Relative to field is set to Release date.

**Transport to supplier:** This is the transport method. This field is only visible when one of the events Relative to field is set to Release date.

**Supplier location:** Working in hand with the 'Originate from' above, FastReact will use the location defined here to calculate the dates of critical path events that are linked to the 'Release date' in those situations where the order is unplanned and so no production location is defined. This field is only visible when one of the events Relative to field is set to Release date.

**Event base date:** This date is used when calculating event target dates for those events that are linked to the Event base date in the Event framework.

**Total working days for production:** This value is used, together with the Transport method above, in the calculation of Release Date, for those orders that are not yet planned In this case FastReact cannot determine on which date an order starts in production so it will use the earliest delivery date, less the number of days you enter here, to make an estimate of this date.

**Inherit events from order:** This drop down menu box allow the selection of an order from which the events will be inherited from.

**Retain target dates / Overwrite events (button):** Once licenced this button will allow for the Retaining of target dates. The button will only be visible when it is licenced. Clicking on the button will set the target date for the selected order. It allows the planners to move/replan an order whilst maintaining the initial target dates.

#### User values

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › User values*

##### User defined text values

An Order may require other information that does not have a pre-defined field. FastReact will allow the creation of additional fields.

**Field:** User data fields must first be defined under the menu option Setup
- General - User defined fields.

**Value:** These fields can be given a value on an Order by Order basis and can then be used for reporting purposes.

**Stock out date:** This value is a user defined date that will allow the Planner to see, on the Planning Board, when stock will run out.

#### Property

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Property*

**Override property match:** This value is used by APS to fine tune the allocation of orders to specific resources. Unlike the Product property this entry can only contain a single value which can be up to 15 characters long.

**Vendor date:** This date is used by APS to fine tune the allocation of orders to specific resources.

- [Icon: Reset Value] Reset the Vendor Date.

#### Forecasting

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Forecasting*

These values can only ever be imported via the FCLinks import file. The values here are defined on the UDF setup.

###### UDF Field(s)

These are the fields that match the Forecast Tree as defined in the UDF setup.

###### Proxy

This is the proxy product that the Forecast Order will take if the Planning Product is not available.

###### Quantity

This is the quantity of the Forecast for this Order. An order can have many Forecasts but the Quantities must equal the Order quantity.

###### Linked

Whither the Order Forecast is Linked to the Forecast or not.

#### Hyperlinks

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Define › Hyperlinks*

This option has been developed to allow communication to an external system to monitor and communicate the status of CP events. This is a weblink storage facility to enable users to directly link, click and open a web browser which would direct straight to the status of that style, order and event.

Additionally, the weblink facility can also be used to connect to other web base storage system such as drop box if the client’s have style imagery stored online.

This functionality allows web links to be stored against a Order. The link behaves like a hyperlink and opens the location, in a browser, when it is clicked on.

The option is enabled via the FRS logon and is found under SETUP - SYSTEM - Order Options.

### Rename

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Rename*

Renaming of an order can take place at any time.

**Select an order to rename:** This is a list of existing Orders. Select the Order that requires renaming from the incremental search list.

**Enter a new name:** Enter a new order name here. FastReact will validate the new order and only allow a rename to be made if the new order reference does not already exist.

**Rename (button):** This button will rename the selected order.

> **Note:** Orders that are attached to a PO cannot be renamed.

### Copy

*Context: Main Menu > Orders > Add and Amend › Orders - Add/Amend › Copy*

**Copy from:** This is a list of existing Orders. Select the Order you want to copy from the incremental search list.

**Copy to:** Enter a new order name here. FastReact will validate the new order and only allow a copy to be made if the new order reference does not already exist.

**Copy order details (button):** This button will only be active when an item is selected and a valid new name has been entered. Click the button to copy the order.

**Include event progress (button):** This button will only be active when an item is selected and a valid new name has been entered. It will include all the events plus it will update any event progress against the order you are copying from.
