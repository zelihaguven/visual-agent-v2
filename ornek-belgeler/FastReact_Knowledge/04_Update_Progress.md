# Main Menu - Update - Progress

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Update > Progress
**Index keywords:** Progress

---

## Update Progress

*Context: Main Menu > Update > Progress › Update Progress*

To keep the planning board and reports up to date the Planner will need to enter Production and Operation updates on a regular basis. With the selection of 'Use combined operation update dialog', check box located in the Setup - Configuration - Production menu the Update Production and Update Operation dialogs are superseded by this new Update Progress dialog.

Updates can either be Incremental or Cumulative.

##### Incremental Updates.

With this type of update the user would enter the amount that was updated for each operation daily.

For example,

| | Operation 1 | Operation 2 | Operation 3 |
|---|---|---|---|
| Day 1 | 100 | 100 | 100 |
| Day 2 | 150 | 150 | 150 |
| Total:- | 250 | 250 | 250 |

The above table shows that there was 100 units made on day 1 and 150 units made on day two to give a total of 250 units.

##### Cumulative Updates.

With this type of update the user would enter the total amount that was updated for each operation.

For example,

| | Operation 1 | Operation 2 | Operation 3 |
|---|---|---|---|
| Day 1 | 100 | 100 | 100 |
| Day 2 | 150 | 150 | 150 |
| Total:- | 150 | 150 | 150 |

The above table shows that there was 100 units made on day 1 and 50 units made on day two to give a total of 150 units.

### Progress

*Context: Main Menu > Update > Progress › Update Progress › Progress*

This Update Progress dialog has some new added features that are turned on via the Sizes option within the new licence environment. These new features are located in Set up - General - Operations and are the check box options:

- Updates progress by size and
- Retain production update details

**Order reference:** Select the order you want to update from the incremental search list.

**Product reference:** This is automatically completed with the selection of the Order reference.

**Order button:** - [Icon: Orders Icon] View Order.

This button will take you directly to the order.

**Progress button:** - [Icon: Progress] View Order progress.

This button will open up another dialog and show the Order Status, so far, for this order.

**Order quantity:** This is the quantity of the order. Next to which is the date field that signifies the date on which the update will take place.

##### Production Updates table

**Operation:** This will be a list of all the operations associated with the Timetable, Order and/or Product. These operations will depend upon the setup configuration.

**Updated to date:** This field is a running total of the amount updated, at each operation, for the order.

**Balance:** This field contains the amount left to process, at each operation, for the order.

**Pending:** This column shows any updates not yet taken into account on the Planning board. Figures will be shown here if you are updating production when the planning board is in use by another user. Normally updates will be incorporated as soon as this dialog is closed.

**Group:** This is the group on the planning board to which the operation has been assigned. Only the Planned Operation, denoted by - [Screenshot: Planned op] , will have a group. Unassigned planned operations will have <Unknown> in the group field.

**Row:** This is the row on the planning board to which the operation has been assigned. Only the Planned Operation, denoted by - [Screenshot: Planned op] , will have a row. Unassigned planned operations will have <Unknown> in the row field.

**Transport method:** This column will only be visible if the 'Include transport method in production update' option is enabled under the Setup - Configure - Production dialog.

**Update:** Enter the production update quantity here. This can either be an incremental quantity or a cumulative quantity to date. This will depend on your preference and is set elsewhere. When an operation has the option 'Updates progress by size' checked on the Set up - Configure - General - Operation set up dialog this function will be enhanced with the introduction of sizes column(s).

This means that, for instance, it allows the input of 2 Large, 3 Medium and 4 Small items rather than the conventional 9 Items. This allows the Planner to visibly see what sizes have been produced as well as the total amounts produced.

**Rejects:** If there are any rejects in any operation they should be entered here.

> **Note:** This is just a text field, it is not used in FastReact production calculations.

**Complete:** Place a check mark in this field to mark the planned operation a completed.

**Comments:** Short notes, up to 80 characters long, can be entered and these will be saved with the update. These notes can then be accessed though the Order Notes dialog.

**Update (button):** This button will update the non-planned operations and mark the planned operations as Pending. The planned operations will not be updated until the Update Progress dialog has been closed.

#### Log

*Context: Main Menu > Update > Progress › Update Progress › Progress › Log*

FastReact will keep a log of the updates as you enter them. This could be useful if you get distracted and loose your place if updating a number of orders.

#### Print

*Context: Main Menu > Update > Progress › Update Progress › Progress › Print*

The log may be printed.
