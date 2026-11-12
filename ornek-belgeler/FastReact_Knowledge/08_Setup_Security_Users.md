# Main Menu - Setup - Security - Users

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Security > Users
**Index keywords:** Users

---

## User Details

*Context: Main Menu > Setup > Security > Users › User Details*

FastReact has its own flexible security to control user access to it's various functions. This is separate to any network security that you may have already. Access rights to view, amend, add or delete both data and configuration settings can be controlled with some detail.

Access to FastReact is controlled through a user name and password. Only recognised Users with a valid password will be able to log into FastReact.

Access rights to functions within Fast react are controlled at the User Group level. Each User must belong to a User Group, however, a User may belong to more than one User Group. Users will have the access rights for any User Group to which they belong. Rights are additive so that Users will have all of the rights assigned to each User Group to which they belong.

This dialog will allow the user to create, amend and delete Users and add new users to existing groups. By default this menu option will only be accessible to the system Supervisor or another user with Supervisor rights.

### Define

*Context: Main Menu > Setup > Security > Users › User Details › Define*

**User name:** Enter the name of a new user or select an existing one from the incremental search list. User names can be any length up to 15 characters.

**Proxy:** Certain values in FastReact can only be updated by a nominated user. When this user is absent (holiday or sickness) the user defined here will be allowed access to perform the updates instead.

**Manager:** This is part of the (optional) work flow system within FastReact which notifies the user's manager if any Development or Production events are late by more than a specified number of days.

**Department:** This is the department of the user.

**E-mail address:** Enter the e-mail address for this user, this will enable the user to receive e-mailed reports and remote data packages.

**Enable Remote Access Services for this user:** When enabled the selected user will be able to receive FR Remote (RAS) packages from FastReact. The user will then appear in the list of available recipient’s when creating a FR Remote (RAS) package.

> **Note:** Once set this option cannot be turned off.

**Scheduled service log recipient:** When enabled this option will tell the FastReact Service user to email a the designated User a report on all the scheduled activities being run.

**Collaborative ID:** When Collaboration is enabled, this option will allow the Users name to appear in the Collaborative partners site against Notes. It reuires the User name to be in both systems in order to work.

**Archive weeks:** Set to 0 to disable, 26 weeks is a minimum value

This option will allow FastReact to Archive each users activity based upon the number of weeks entered in this field.

**Insert (button):** This button will insert or update the User.

**Delete (button):** This button will delete the selected User.

**Clear password (button):** This button will clear the password for the selected User.

### Rename

*Context: Main Menu > Setup > Security > Users › User Details › Rename*

Renaming of a user can take place at any time.

**Select a user to rename:** This is a list of existing Users. Select the user that requires renaming from the incremental search list.

**Enter a new name:** Enter a new user name here. FastReact will validate the new user and only allow a rename to be made if the new user reference does not already exist.

**Rename (button):** This button will rename the selected user.

### Groups

*Context: Main Menu > Setup > Security > Users › User Details › Groups*

Users may be added to existing user groups here

#### Select a user from the list

*Context: Main Menu > Setup > Security > Users › User Details › Groups › Select a user from the list*

Click on a user to select from this list; the user name will be shown at the top centre of the dialog as confirmation.

#### Is a member of

*Context: Main Menu > Setup > Security > Users › User Details › Groups › Is a member of*

This list shows the groups to which the user currently belongs. Users that do not belong to a group will not be able to use FastReact.

#### Available groups

*Context: Main Menu > Setup > Security > Users › User Details › Groups › Available groups*

This list shows previously defined user groups. The planner can add users into groups by dragging the group from this list to the 'Is a member of' list. The planner could also double click on the list to add the group to the selected user. Users can be removed from a group in a similar way.

**Update (button):** This button will update the user group.

### Proactive Desktop

*Context: Main Menu > Setup > Security > Users › User Details › Proactive Desktop*

This is a licence option and when enabled allows the selected user access to instant information direct to the FastReact desktop. This information will be in graphical form.

**Select a user to update:** Select the user, from the drop down menu, who will have this configuration of desktop objects.

**Show Proactive Desktop:** When this is check the selected user will have access to the Proactive Desktop.

#### Available Categories

*Context: Main Menu > Setup > Security > Users › User Details › Proactive Desktop › Available Categories*

These are the desktop objects that are available within the Proactive Desktop. All of the objects below are multi-configurable depending upon the users perspective.

**Work in Progress:** This object will graphically depict the WIP status based upon criteria setup within the Proactive desktop.

**Orders:** This object will graphically depict the Order status based upon criteria setup within the Proactive desktop.

**Flows:** This object will graphically depict the Flow status based upon criteria setup within the Proactive desktop.

**Events:** This object will graphically depict the Event status based upon criteria setup within the Proactive desktop.

**Transport:** This object will graphically depict the Transport status based upon criteria setup within the Proactive desktop.

**Material:** This object will graphically depict the Material status based upon criteria setup within the Proactive desktop.

**Capacity:** This object will graphically depict the Capacity status based upon criteria setup within the Proactive desktop.

**Bottleneck:** This object will graphically depict the Bottleneck status based upon criteria setup within the Proactive desktop.

**Analysis:** This object will graphically depict the Analysis status based upon criteria setup within the Proactive desktop.

**Update (button):** This button will update PAD for the selected User.

### Customer groups

*Context: Main Menu > Setup > Security > Users › User Details › Customer groups*

**Select a user to update:** Select the User that requires access rights.

**Deny access to these customer groups:** This is a list of the groups that were defined on the Customers dialog. An explanation of the settings can be found here.

**Update (button):** This button will update access level for the selected User.
