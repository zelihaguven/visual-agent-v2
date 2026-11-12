# Functionality - Planning Methodologies - Batch (Tandem) Planning

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Planning Methodologies > Batch (Tandem) Planning
**Index keywords:** Batching

---

## Batch (Tandem) Planning

Batches can be monitored at Low Level where each ‘planned’ order will represent the entire Batch but will reference the Parent Order only. This ‘planned’ order will be suffixed with a ‘+’ on the strip to donate the fact that it is a Batch. The child orders in the Batch will have their strip ‘crossed out’, resembling an envelope, this donates that the strip, Child Order, is part of a Batch.

A list of all Child Orders can be viewed on the Hint window whenever the cursor hovers over the Parent (Batch) Order.

The Batch strip colour will take the worse case scenario of all the delivery dates regardless of whether the order is a Parent Order or a Child Order.

When creating the Batch the main or Parent Order should be created first and the subsequent sub or Child Orders can then be created with the nominated Parent Order referenced in the ‘Process with’ field of the Order Add Amend dialog. Only one Parent Order can be nominated on each Child Order.

[Screenshot: Batch]

Using the Drop Down Low Level option allows the planner to see the Child Orders. Notice that the Parent Order, 12345A, has a ‘+’ after its name. This donates that the strip is a Batch strip and dropping down the row shows all the Child orders contained in that batch.

The Child Orders strips in the Batch all look like envelopes. These Child Orders cannot be replanned individually, although they can be altered using the right click functionality. This does not alter the Child Order strip as the strip size is taken from the Parent Order regardless of any other factor.

Hovering the cursor on the Parent Order (Batch Strip) allows FastReact to display the Hints window. This Window will list all the Child Orders associated with the Parent Order.
