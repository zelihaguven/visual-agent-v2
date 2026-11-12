# Main Menu - Tools - Utilities

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Tools > Utilities
**Index keywords:** Utilities

---

## Utilities

*Context: Main Menu > Tools > Utilities › Utilities*

This option gives access to a variety of tools and other functions, some of which can only be enabled by a Fast React representative.

### Maintenance

*Context: Main Menu > Tools > Utilities › Utilities › Maintenance*

FastReact will lock certain functionality whilst it is performing long processes or when plans being changed. This will prevent the inevitable errors and confusion if two users try to perform conflicting actions.

**Clear plan locks (button):** FastReact will lock planning boards if opened with full access allowing the planner to make and save changes. At this time the plans will not be available to other users except as read only plans. If FastReact terminates unexpectedly (e.g. power failure) these locks will remain in place leaving all plans as read only. This option is provided to clear these locks after such a failure.

**Clear material plan locks (button):** The materials planning board is essentially single user only. When it is opened with by a user with full access FastReact will apply a lock to prevent other users accessing it except as read only. If FastReact terminates unexpectedly (e.g. power failure) this lock will remain in place leaving the plan as read only. This option is provided to clear the lock after such a failure.

**Clear import/export lock (button):** FastReact will apply a lock so that only one computer on a network can initiate a data import process. If FastReact terminates unexpectedly (e.g. power failure) this lock will remain in place preventing another import procedure to be started. This option is provided to clear the lock after such a failure.

**Clear user log on (button):** FastReact marks a user as logged on, then clears this when that user logs off. This is to prevent problems that could occur with planning data integrity if the same user logged on to two different computers on a network. If FastReact terminates unexpectedly (e.g. power failure) the user will appear to be still logged on and will not be able to re-log on until this is cleared. This option is provided to clear the user log on after such a failure.

### Database

*Context: Main Menu > Tools > Utilities › Utilities › Database*

#### Purge functions

*Context: Main Menu > Tools > Utilities › Utilities › Database › Purge functions*

These options are provided to clear data from your database. You will need supervisor rights to access these and should be used with great care as large quantities of data can be permanently removed.

**All order related data (button):** This option will remove all order related data, however all product data will remain.

**All product and order related data (button):** This option will remove all product and order data, leaving general set-up and other data intact. This would be useful if clearing down between seasons.

**Materials stocks and deliveries (button):** This will remove all material stocks and deliveries leaving the base material data intact

**Unused materials (button):** This will remove any material that is no longer used in a Bill of Materials on an order or product and that has zero stock and has no outstanding deliveries or has deliveries which are more than 90 days overdue.

#### Other functions

*Context: Main Menu > Tools > Utilities › Utilities › Database › Other functions*

**Execute SQL statement (button):** This allows competent users to make changes to the database using an SQL statement.

> **Note:** Be careful as this is an extremely powerful command option and, as such, if misused could create significant database problems.

The User can also execute 'select' statements to view database contents. The data returned from the select statement can be saved to a CSV file which can then be opened outside of FastReact using Excel or a file editing program.

### Index repair

*Context: Main Menu > Tools > Utilities › Utilities › Index repair*

**Defragment (button):** This button will defrag the Live database. This will perform reorganisation and rebuilding of indexes when the button is clicked. This could improve performance and speed.

> **Note:** This may take a long time, depending upon the size of the database.

Show advanced options

Enabling this option will unhide the Advanced Options.

> **Note:** It is strongly recommended that the advanced options are not used, unless requested to by Fast React.

**Analyse (button):** This button will analyse and list all the issues found in the database.

### Verification

*Context: Main Menu > Tools > Utilities › Utilities › Verification*

These options are provided to force a data verification check. As FastReact verifies its own data each time it is started you should not have to use any of these functions.

> **Note:** Only use the option in this are under specific instructions from Fast React.

### Calculators

*Context: Main Menu > Tools > Utilities › Utilities › Calculators*

These options are provided for testing and would probably not find any use on a day to day basis.

#### Colour calculator

*Context: Main Menu > Tools > Utilities › Utilities › Calculators › Colour calculator*

This allows the user to convert any colour into its Red-Green-Blue components.

#### Date calculator

*Context: Main Menu > Tools > Utilities › Utilities › Calculators › Date calculator*

This allows the user to convert any date into the numeric value that FastReact uses.

### Restore plan

*Context: Main Menu > Tools > Utilities › Utilities › Restore plan*

FastReact can optionally make a backup of planning boards each time you save a plan. This backup is made to your local hard disk in 'C:\Fast_React\Backup'. (The backup file is of type '.DAT' and is in binary format which cannot be interpreted in Notebook etc). FastReact will retain backups for a week, after which they will be deleted.

In the event of a system failure or other problem you can restore a backup of a previously saved plan. Select a planning board to restore.

> **Note:** The High Level and Low Level boards are listed separately.

You will also need to select a section if you have more than one defined. Click the 'Find' button and FastReact will list all of the backups that you have made. Select a backup and then click the 'Restore' button.

At this stage you have only restored the backup to your own workstation. To make the restored plan permanent you must open the selected board and force FastReact to save it. The simplest way to do this is to click on a strip and put it down again in its original position.

The advantage to this approach is that you can restore old plans and run reports against this plan with no danger of overwriting the Parent plan. All of the normal security and multi user controls will be in effect to prevent users who have no planning rights from restoring a backup to the database.

> **Note:** Only use the option in this are under specific instructions from Fast React.

### Configure Restore

*Context: Main Menu > Tools > Utilities › Utilities › Configure Restore*

Use these options to restore text based configuration files to the local hard disk from a backup. This is particularly useful when testing importing in a Test system.
