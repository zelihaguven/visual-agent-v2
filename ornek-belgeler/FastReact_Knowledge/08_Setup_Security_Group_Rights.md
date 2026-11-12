# Main Menu - Setup - Security - Group Rights

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Security > Group Rights
**Index keywords:** Group Rights

---

## User Group Rights

Once you have created your user groups you can assign rights to each group.

> **Note:** By default user groups have no rights so will not be able to access any useful FastReact functionality.

There are tabs to assign general menu access rights, to assign planning rights and to monitor users who are currently logged on.

### Functionality

**Select a user group:** Select from the list the group you want to modify..

#### Check those option that the user can access

This is a list of the available main menu options and some sub menu options. By default new user groups will not have any access to functions. The administrator/FastReact Implementer can allow access to selected functions by placing a tick in the box next to the function name. Change functions will allow a user group to create or modify an existing record whilst Delete functions allow users groups to do just that.

Whist the above relate to menu options the options below are system wide in nature:

**Allow access to financial data:** All financial information will be hidden from users in this group. This includes all data shown on entry dialogs and values returned in reports.

**Supervisor rights - allows access to all functions:** Users in this group will have access to all functionality as if they were system administrators. Use this option with care!

### Planning

Use this option to define the access rights to planning board data.

**Select a user group:** Select from the list the group you want to modify..

#### Planning board and Section list

This is a list of planning boards and sections available to the selected user group.

- [Icon: Access full] Group will have full access.

Planning boards and sections with a plan icon placed against them are full access.

- [Icon: Access view only] Group will be view only.

Planning boards and sections with a lock placed against them are view only.

- [Icon: Access view only] Group will be unable to move strips.

Planning boards and sections with a open lock placed against them are full access but Groups which have this set will not be able to move strips.

- [Icon: Access none] Group will have no access.

Planning boards and sections with a cross placed against them will not be visible at all

Double click on the icon to change access rights

### Users logged on

This gives a list of those users that are currently logged on and the date/time that they started FastReact. This can be useful to system Administrators when they need to update the FastReact program or perhaps backup the database.

**Allow users to log themselves off after a system failure:** Normally FastReact will not allow a user to log on twice, either on two different workstations, or as two FastReact sessions on the same workstation. However, if FastReact terminates unexpectedly, either though a network problem, power failure or FastReact program malfunction, the user will still be logged on in the database. In this situation only the system supervisor can log off the user through the Maintenance option on the Tools menu. If this proves inconvenient, the administrator can select this option and this will allow a user to log themselves off.

However, please be aware that this will not close another FastReact session on another workstation. This could mean that the user could make changes on two different machines and these could conflict with each other. This could be especially damaging if the user has full planning rights.
