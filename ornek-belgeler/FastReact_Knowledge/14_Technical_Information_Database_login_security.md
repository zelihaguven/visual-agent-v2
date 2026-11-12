# Technical Information - Database login security

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > Database login security

---

## Login Security

Microsoft SQL Server requires that all connections are validated though a user name and password combination to prevent unauthorised access to data.

This can be configured to use the security settings from the operating system (Windows NT or higher) or though its own internal security system. By default the latter will be used if your database has been installed by FastReact staff.

As supplied SQL Server has an administration user account defined called 'sa' (for system administrator). This account is initially not protected by a password giving unlimited access to anyone who connects to the database with this name. This is not a situation that is recommended as you would leave your database open to tampering and certain computer viruses have been known to attack unprotected SQL Server databases using the 'sa' account. For this reason we would recommend that you apply a password to the 'sa' account (make sure you do not forget it) and create a new user account called 'FastReact'.

By default FastReact will try to use the 'sa' account, but can be configured to use the 'FastReact' account. See also Create new database.
