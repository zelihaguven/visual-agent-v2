# Main Menu - Tools - Send Collaborative Package

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Tools > Send Collaborative Package
**Index keywords:** Send Collaborative Package

---

## Collaborate

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate*

This dialog will manually send the Collaboration package to the remote site.

### Collaborate

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate › Collaborate*

**Select package to send:** Select, from the list, a package to send.

**Description:** This is a description of the package as defined on the configure dialog. (see below).

**Send to:** This is the pre defined recipient.

**Collaborate (button):** This button will email the collaboration data.

### Configure

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate › Configure*

**Package name:** This is the collaboration package name.

**Description:** This is a description of the collaboration package.

##### Select group(s) to send to remote planner

This is a list of all the groups to which the package can be sent.

##### Select a host company to receive plan changes

This is a drop down list of host companies which can receive the collaboration package. The remote site would have the host company name here.

> **Note:** The above two 'Select…' options are mutually exclusive and as such cannot be both enabled in the one system.

#### Options

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate › Configure › Options*

**Do not allow replanning after package send:** This should always enabled at a Host site as the planning control will be under the Remote site. Never enable this option at the Remote site.

**Send all products:** With this option enabled, all Products will be collaborated regardless of wither or not they are attached to an order or even if they are previously collaborated products.

**Send all changed products:** This option is similar to the above one apart from the fact that it will only send products that have been updated since the last collaboration.

**Skip Confirmed/Provisional/Speculative/Transit/Suggested orders:** This option will not collaborate orders with selected order status.

**Send group details:** This option will send the Group details to the collaborating partner.

**Send group names:** This option will send the Group name to the collaborating partner. This name can then be reported and displayed on the Planning Board.

**Send row names:** This option will send the Row name to the collaborating partner. This name can then be reported and displayed on the Planning Board.

**Send order/product BoM:** This option will send the Order and Product BoM. This will make the sending package huge.

**Send consolidated row capacity:** This will send the consolidated row capacity from the Remote site to the Host site allowing the Host site visibility of the planned Order, factory capacity and factory loading.

**Hide customer details:** With this option enabled, the recipient of the data package will be unable to see any customer details.

**Skip planning data return:** This option would only return production updates, event updates etc. but not any replanning.

**Send order and product use defined fields:** This option will send over the alpha-numeric UDF fields.

**Unload non planned orders from HL board:** This option will unload any order that have been returned to the Host site in a collaborative planning system but have never been planned at the remote site.

**lock agreed flows (at remote):** This option will lock the agreed flows at the Remote site.

**lock original flows (at remote):** This option will lock the original flows at the Remote site.

**Send order financials:** This option will send order financial UDFs to the receiving side.

**Delegate financials (Price & Cost):** This option will delegate the control of the default financial UDFs to the collaborative partner.

**Save package and handshake to folder:** This is the folder in which the sent package, going to the collaborated partner, will be saved in.

**Associated Collaboration name:** This is name of the system to which the Package belongs.

> **Note:** The above two options can be used instead of email. This is particularly beneficial when setting up collaboration test environments.

**Send package to email address:** This is the email address to which the package will be sent.

#### Handshake

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate › Configure › Handshake*

##### Current package

This is the number of packages received.

##### Last handshake

This is the package number of the last fully collaborated package.

**Reset Handshake (button):** This button will reset the above two numbers to "0" thereby forcing FastReact to send everything over to the selected collaborative partner. This will drastically increase the size of the Collaborative email package and as such it may not get through some email systems.

**Update (button):** This button will update the package configuration data.

**Delete (button):** This button will delete the package configuration data.

### General

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate › General*

#### Options

*Context: Main Menu > Tools > Send Collaborative Package › Collaborate › General › Options*

**Disallow Confirmed/Provisional/Speculative/Transit orders to have production updates:** These option will disable the use Productions Updates for the selected Order Status in the current system.

**Suppress Company identifier suffix in planning boards and reports:** This option will hide the "==<Identifier>" defined under Setup - Configure - General on all reports and Planning Boards.

**Prevent order substitution this system:** This option will prevent the system for substituting orders.

**Delegate control of delivery date for Confirmed/Provisional/Speculative/Transit orders:** These options allow the enabled system to delegate the control of the Order delivery date to the collaborative partner.

**Delegate control of order user status:** This option will allow the enabled system to delegate the control of the Order Extended Status to the collaborative partner.

**Delegate control of product colour:** This option will allow the enabled system to delegate the control of the Product Colour to the collaborative partner.

**Log file folder:** This is the selected folder that the collaborated log file will be saved in.

**Save (button):** This button will save the package configuration data.
