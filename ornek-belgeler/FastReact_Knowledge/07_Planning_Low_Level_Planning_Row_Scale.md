# Main Menu - Planning - Low Level Planning - Row Scale

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > Low Level Planning > Row Scale
**Index keywords:** Row Scale

---

## Row scale

### Low Level Planning Board

The row scale runs down the left hand side of the Low Level planning board and lists the resources that are associated with the open Planning board and the selected Section within that board.

[Screenshot: LL Row scale]

### Row height

The height of each row on the planning board can be set to one of four values each offering a different degree of detail. The row height can be controlled by clicking on the blue Up and Down buttons at the left of the tool bar.

At the minimum height no detail can be shown, but any colour coding associated with the row is retained.

At the medium height text and numbers are shown as discussed below.

At the largest heights additional data is shown as there is enough room for two lines of text.

### Status scale

The very left hand column of the row scale is where FastReact shows the consolidated status for orders planned on each row. The status includes the total number of days late against delivery dates (shown against a blue background) and/or the total number of days early against the critical path targets (shown against a yellow background).

At the full row height FastReact will show both of these values, however, with a smaller row height there is just not enough room to display two numbers so FastReact will only show one of these. If there are late deliveries on that row then FastReact will always show this. If all orders are on time then FastReact will show just the number of early days. If there are no problems at all then FastReact will just show the number of strips on each row, against a white background.

The benefit of the status scale becomes apparent when you have many orders planned over a long time period and you have scaled the planning board to only show a small period. If there are any problem orders then you will be able to see this in the status scale even if you cannot see the orders themselves.

### Strip list

Clicking on the status scale for any row will result in FastReact displaying a list of all the strips that are planned on that row. See Row scale Strip list.

### Row details

The main part of the row scale shows the Row Name followed by the Capacity (per hour) in red and the Throughput time (days) in blue. The width of the row scale can be adjusted by dragging (with the mouse) the red line between the row scale and the planning board until this data is fully visible.

If the row height is at its fullest then additional information is shown below the row name. This will normally be the Group to which the row belongs, however you can change this by sorting the rows into a different sequence. See below.

Finally the row default Capacity factor is shown in dark red underneath the row capacity.

### Sorting rows

By default FastReact displays rows on the planning board in alpha numeric sequence based on the row name. A particular sequence can be forced by prefixing row names with numeric values when the rows are created. The prefix is used to sort rows even if the prefix is hidden.

Each row can also have other values such as a Property and a Factory. These values can also be used as the prime sort sequence with rows within any Property or Factory sub sorted by row name.

When sorted by Property or Factory this value is shown underneath the row name. If any rows have missing values then the Group is displayed instead (in grey and lowercase) but the group is not used in the sort. Such rows are sorted to the bottom of the planning board.

### Deleting rows

You can delete rows from within the planning board, but only if you have rights to do so and only if the planning board has been saved.

### Drop down display

The planning board rows can be Dropped down, that is each strip can be displayed on its own row. This is useful if your strips are very short as this allows the details for each to be easily seen. If this type of display is enabled on the Setup - Planning dialog, then the row scale will contain a drop down arrow. Click the resultant arrow on the planning board to expand or collapse the row.

### Row colours

The rows are normally displayed with a white background. If the row is marked as a Holding Row then the background will be yellow to allow it to be easily identified. When loading a new order, the right hand side of the row may turn red. This visually shows the Planner that the strip cannot be planned on this row.
