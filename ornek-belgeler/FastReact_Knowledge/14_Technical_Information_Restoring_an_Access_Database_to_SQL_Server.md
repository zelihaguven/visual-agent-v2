# Technical Information - Restoring an Access Database to SQL Server

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > Restoring an Access Database to SQL Server
**Index keywords:** SQL Server

---

Before attempting this procedure please contact your FastReact support desk for more information.

This is not a common procedure as you would either run SQL Server OR Access, not both. For this reason the procedure is somewhat messy.

Follow the steps below and stop if an error is reported at any stage.

## Create a NEW SQL Server database in Enterprise manager or within FastReact.

Backup your existing database.

## Start FastReact on this new database so FastReact can create the database structure.

This will include the tables and primary keys and table indexes. You must not miss out this stage, even though the procedure will appear to work without it. However, when you copy the data from Access (below) the SQL Server tables will not be properly structured.

## Open the new database and empty the following tables

_LOOK_UP_TABLE,

_NUMBERS,

_USER_SETTINGS,

_USERS,

_REPORT,

 _AUDITTRAIL ,

These tables are initialised with data when FastReact starts and, if not emptied, you will get a duplicate key error when importing data.

## Using Enterprise manager right click on the database and select ' All tasks ' then select ' Import data '.

Follow the instructions on the Import data wizard and make sure that all tables are imported without errors.
