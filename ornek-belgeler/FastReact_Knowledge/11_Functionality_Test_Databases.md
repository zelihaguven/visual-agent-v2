# F unctionality - Test Databases

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Test Databases
**Index keywords:** Test Databases

---

## Test Databases

*Context: Functionality > Test Databases › Test Databases*

Creating Test Systems are an integral part of any FastReact project. Not only does it allow the FR Implementer to test and finalise their configuration prior to Go Live, it also allows the Client to test and get a feel for the product in a safe environment.

With this in mind Fast React Systems have developed functionality to create a Test system based upon the Live environment and Licence this test system.

There are a few caveats to the creation of this Test system:

- The SQL Test instance must already exist on the same SQL server.
- FRLSMgr must be reinstalled with the new improved version and configured to Licence the Test environment.
- Only users with Supervisor rights can create a Test environment.
- Once a Test environment is created it is a stand alone, separate entity and does not interact with the Live environment.

### Create the SQL instance

*Context: Functionality > Test Databases › Test Databases › Create the SQL instance*

The first thing to do is to ensure that there is an SQL instance set up within SQL Server for the Testing environment to be created on. If there is not one there then create one:

[Screenshot: Test DB Instance]

**Note:** Do not create any FR tables and do not log on to this Instance with Evolve/Align.

### Setting up FastReact Licencing

*Context: Functionality > Test Databases › Test Databases › Setting up FastReact Licencing*

Download the new FR Licence Package, and double click to install it. If there is already an instance of the Licence Service or Manager running then the new install will stop it and over write the old version.

#### Configure the FRLSMgr

*Context: Functionality > Test Databases › Test Databases › Setting up FastReact Licencing › Configure the FRLSMgr*

Double click on the FRLSMgr executable to start the Manager:

[Screenshot: FRSLMgr]

This will start the Licence Manager running and there will now be a red FR icon in the bottom left of the screen (near the PCs system clock):

[Screenshot: Red Manager icon]

Right click on this icon and select, “Configure Licence Server”:

[Screenshot: Configure]

This will display the Manager Configuration dialog. There are 3 parts to this dialog:

1. The details of the dongle plugged in to the Server that FRSLMgr is running on.
2. The database names.
3. The Network location of the of the Licence file.

[Screenshot: FRSLMgr Dialog]

The new area is in part 2: Users can now define a Test Database to Licence. This Test database will already exist in SQL Server.

**Note:** The Test database will only ever be licenced for one month, after which time a new Test database will need to be created.

The resulting FRLSMgr setup will look similar to this:

[Screenshot: FRSLMgr Dialog]

After clicking on the Apply button the FRLSMgr icon will now be flashing Green and Yellow or it will be Green:

[Screenshot: Green Manager icon]

### Create the FastReact shortcuts

*Context: Functionality > Test Databases › Test Databases › Create the FastReact shortcuts*

Shortcuts now need to be created in order to access the two different system:

The Live environment.

The Test environment.

In Windows Explorer, locate the FR4.exe program file and right click on this and select “Create shortcut”:

[Screenshot: Create shortcut]

This will need to be done twice: once for the Live environment and once for the Test environment. Next, right click on the shortcut and select “Properties”:

[Screenshot: Shortcut properties]

In the resultant Properties dialog for this Shortcut enter the required parameters:

[Screenshot: Shortcut properties done]

The recommended parameters to use are:

1. **SN:<Server_Name>** - This is the server name where the DB instance is located. This parameter is optional, if there is only one Server then there is no need to include it.
2. **DB:<Database_Name>** - This is the name of the Database. This parameter is mandatory and must be added to the Target field as per the above image.
3. **/USELS** - This must be on all shortcuts that are run from the Server as it forces FR to use the Licence details as defined on the FR Manager (FRLSMgr) program rather than using the Dongle that is plugged into the server.

### Creating the Test Environment

*Context: Functionality > Test Databases › Test Databases › Creating the Test Environment*

#### Populating the Test Database

*Context: Functionality > Test Databases › Test Databases › Creating the Test Environment › Populating the Test Database*

Once the shortcuts have been created and configured and the SQL instance created on the SQL Server, the Live environment can be used to create the Test environment.

**Important Note:** Please ensure that all users are logged out of Evolve/Align before proceeding

Log in to Evolve/Align with Supervisor rights and go to TOOLS - Populate test database:

## [Screenshot: populate test db]

*Context: Functionality > Test Databases › [Screenshot: populate test db]*

This will result in the populate test database appearing where the User can enter the SQL DB name and the server on which this instance is running:

[Screenshot: populate test db]

**Note:** Unlike WhatIf databases, the Test database is a true standalone multi user environment

**Note:** Only one Test database can be Licensed at a time.

If the Test database had already been in use, FastReact will warn the User and ask if it is ok to clear the existing DB:

[Screenshot: Existing DB]

If the User is happy to clear the existing Test DB and re-populate it then they would click on Yes. After the Test DB has finished they will then receive a message to say its done:

[Screenshot: Test DB created]

**Note:** Test databases are only valid for one month and this cannot be extended.

### Logging on to the Test environment

*Context: Functionality > Test Databases › [Screenshot: populate test db] › Logging on to the Test environment*

The Test database has now been created and populated with data from the Live environment, we mow need to log off of the Live environment and log into the Test environment via the Shortcut that was created earlier:

[Screenshot: Test shortcut]

This will display the log on screen for the Test database, enter the User Name and Password and log on to this Test environment:

When you have logged on to the Test Environment the FastReact menu bar will also indicate that the User is logged on to the Test environment:

### Caveats and preventative measures

*Context: Functionality > Test Databases › [Screenshot: populate test db] › Caveats and preventative measures*

In the Test environment there are a number of caveats and preventative measures in place so that data does not get confused with the Live environment:

- The email settings are cleared.
- If email is reconfigured, a warning dialog will appear to make the user aware that they are sending an email from the Test environment.
- The collaborative email settings are cleared and disabled.
- Email.
- Send collaborated package.
- Receive collaborated package.
- Import settings are re-set to C:\Fast_React\Imports.
- Export settings are re-set to C:\Fast_React\Exports.
- Reports have “Test System” in their headers.
- Test environments cannot replace the Live environment.
- Test environments only last for 1 month and cannot be extended.
