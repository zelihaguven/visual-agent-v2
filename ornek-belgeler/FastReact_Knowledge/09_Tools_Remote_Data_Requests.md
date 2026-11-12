# Main Menu - Tools - Remote Data Requests

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Tools > Remote Data Requests
**Index keywords:** Remote Data Requests

---

## Send Remote Data Requests

When licenced this option will allow the Host system to send data packages out to remote sites. This will allow the remote site to update progress, operations, events etc. and if enabled return the data to the Host site. This allows the Host site to have an overall picture of the planning environment, whilst giving the remotes sites autonomy.

### Send package

**Package name:** This is the name of the remote package that is to be sent, as defined on the define package tab.

**Send to:** This is the default name of the recipient as defined on the define package tab.

**Status:** Once the Send package button has been clicked this area will display details regarding the status of the sending.

**Send Package (button):** Click to send the package.

### Define package

**Package name:** This is the package name. The user can either select a package from the drop down list or define a new package by creating a new name.

**Email text message:** Any text in this field will appear on the email to which the package is attached.

**Simple package sent to individual users:** This option will send a package to all selected users.

**Recipient:** This is a drop down list of users as created in the Security - Users section.

#### Other Users

Additional user can be select to view the remote package.

**Production days to send:** This is the number of production days that will be form the remote package.

**Event days to send:** This is the number of event days that will be form the remote package.

#### Content

**Planned schedules:** If this is checked the remote package will include the Planned schedules. This will allow the remote user to access and alter the planned schedules.

**Operation schedules:** If this is checked the remote package will include the Operation schedules. This will allow the remote user to access and alter the operation schedules.

**Order events:** If this is checked the remote package will include the Order events. This will allow the remote user to access and alter the order events, as defined in the Framework.

**Development events:** If this is checked the remote package will include the Development events. This will allow the remote user to access and alter the development events, as defined in the Framework.

#### Options

**Hide delivery dates:** By checking this option the remote user will be unable to see that delivery date for the orders.

**Hide customer details:** By checking this option the remote user will be unable to see that customers details for the orders.

**Hide work content:** By checking this option the remote user will be unable to see that work content for the orders.

**Include skipped events:** By checking this option the remote user will be able to see any skipped events on the orders.

**Send completed operations:** By checking this option the remote user will be receive all completed events as well as uncompleted events.

**Exclude Confirmed orders:** Confirmed orders will not be included in the package.

**Exclude Provisional orders:** Provisional orders will not be included in the package.

**Exclude Speculative orders:** Test orders will not be included in the package.

**Exclude Transit orders:** Transit orders will not be included in the package.

**Include Public documents:** By checking this option the remote user will have any documents, that have been attached to orders, products, etc, attached to the remote package. Only documents pertinent to the remote package will be sent.

**Allow remote to change availability:** By checking this option the remote user will have the ability to change availability for the orders on the remote package.

**Allow any user to update events:** By checking this option the any remote user will have the ability to update all the events.

**Send User Defined Fields:** User defined fields will be included in the package.

#### Include operation schedules

This will be a list of all the operation, including the planned operation(s), which are part of the host system. These operations are defined in the Setup menu. There is an option to select each operation.

#### Include groups

This will be a list of all the groups which are part of the host system. These groups are defined in the Setup menu. There is an option to select each operation.

#### Override automatic selection

This is a list of all events set up in the host system. This includes development events and production (order) events, (if enabled). There is an option to override the sending of these against each operation.

**Update (button):** This button will insert a new package or update the package details.

**Delete (button):** This button will delete the selected package.
