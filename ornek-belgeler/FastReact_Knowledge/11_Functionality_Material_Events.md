# Functionality - Material Events

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Material Events
**Index keywords:** Material Event

---

## Material Events.

FastReact has a powerful event reporting mechanism that can schedule your key activity dates around production plans. By circulating the target dates amongst those responsible you can ensure that all staff are working to a common task set, arranged in priority sequence, and thereby giving production the best chance of starting on time.

This mechanism can be expanded to include items on your Bill of Materials so that each can also have target dates. This provides a simple way to schedule materials purchasing without going to the complexity of a full MRP system.

### How it works

You can create a list of broad Material groups such as 'Fabric', 'Trims', 'Packaging' and so on. Each of your materials can then be associated with these groups in a logical fashion. The association should group materials around the point in the production process at which these materials are required. So in the examples above 'Fabric' would be normally needed before 'Trims' and 'Packaging' would normally be required at the end of the production process. As a by product of this grouping your material reports can be sorted and filtered by the group so that a report could just show 'Trim' materials.

When setting up your Event framework each event can be linked to a material group. This will provide a target date for all materials on the relevant order to be taken from the target date for the associated event. So using the examples above you may create an event called 'Order fabric' and link this to the 'Fabric' material group. An order has two different fabrics and the target date for the 'Order fabric' event (calculated in the normal way) is 10th August. FastReact will show these two fabrics in the list of events with a target date of 10th August. You can update of the expected dates and completed dates of this event for each of these fabrics in the normal Update event menu.

You can also report target, expected and completed dates together with the number of days late (or early) for your materials.

### Restrictions

Materials must be entered against each order, and not against products as the expected and completed dates are order specific.

### Points to consider

FastReact will only report materials that:

- Have a valid material group;
- Have an event that is linked to that group;
- Have the relevant events enabled in the timetable attached to orders.
