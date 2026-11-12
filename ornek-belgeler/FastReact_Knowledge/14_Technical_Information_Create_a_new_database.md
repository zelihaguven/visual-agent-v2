# Technical Information - Create a new database

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > Create a new database
**Index keywords:** Create

---

## Create a new database

A new database can be created from within FastReact so that you do not need to have, or understand, any third party tools.

FastReact supports Microsoft SQL Server and Microsoft Access and, although FastReact can be used with other databases as well, it cannot create these other types.

The procedure to create a database is simple but is a little different for the two database types.

### SQL Server database

At the user log in screen click the Change button.

**Database name:** Enter a new database name. Do not use spaces or other invalid characters.

**Server name:** Enter the name of the file server on which you want to create the database. The file server must already have Microsoft SQL Server running.

**Log in name:** Do not enter anything here. By default FastReact will create a user login for you called 'FastReact'. You should not change this unless you understand the consequences.

Click the Create button.

**Enter new database name:** This will show the name of the database you have just entered. You can change it here if you want to.

**Enter server name:** This will show the name of the server you have just entered. You can change it here if you want to.

**Directory to contain data file:** Enter the location of the new database data file. This can be anywhere on your network but it would be better to be on the fileserver so that it will be secure and properly backed up. You can create a new directory here if you want.

**Directory to contain log file:** This file can be in the same location to the data file or in a different location if you want. Keeping them in the same location is more convenient, but you could put the data files on one physical hard drive or computer and the transaction logs on another hard drive or computer. Performance will be improved somewhat and you will be better protected against a hardware failure.

**System administrator's name:** You will need to connect to the 'Master' database in SQL Server before you can create a new database. To be able to do this you need to log in to SQL Server with system administrator rights. The default name is 'sa' but for security you may have changed this. Enter the system administrator's name.

**System administrator's password:** As supplied SQL Server does not have a password on the 'sa' account. Microsoft advise that a password is created for this account for security reasons. If you have a password on the above account then enter it here.

Click Create database

This will create new database files in the locations you have specified and register the new database in the 'Master' database on the specified server. It will also create a Login called 'FastReact' and give that login sysadmin rights to allow it to create and manage your new database. The 'FastReact' login does not have a password.

**Login name (Sql Server):** The login name is saved in the Registry on each workstation. By default FastReact will use the 'FastReact' login, so you should not need to make any changes on other workstations. However, you can change the login to a different name by entering in this field and pressing the Update button. This will change the Registry settings so that this login name is used from this time. You will need to do this on all workstations that need to access FastReact.

> **Note:** The new database will be created with the 'Simple' database Recovery method. This is convenient to maintain and offers good security. If you prefer better loss recovery capabilities you should change this to the Full Recovery method in the Database Properties in Microsoft SQL Server Enterprise Manager. See the Microsoft documentation for more details.

If the database is created correctly a message box will say so. Click Ok and you will return to the previous screen. Click Update to tell FastReact to use this database from now on.

### Access database

At the user log in screen click the Change button.

**Database name:** Enter a new database name. You can add the file extension '.MDB' if you want. Do not use spaces or other invalid characters.

**Directory to contain data file:** Enter the location of the new database data file. This can be anywhere on your network but it would be better to be on the fileserver so that it will be secure and properly backed up. You can create a new directory here if you want.

**Click Create database.:** This will create a new database in the location you specified. An error will be reported if the database already exists.

If the database is created correctly a message box will say so. Click Ok and you will return to the previous screen.

Click Update to tell FastReact to use this database from now on.
