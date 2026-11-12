# Functionality - Planning Methodologies - Collaborative Planning

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Planning Methodologies > Collaborative Planning
**Index keywords:** Planning Methodologies, Collaborative Planning

---

## Collaborative Planning

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning*

The ideas behind this product development is:

1. To allow greater autonomy between factories whilst maintaining a level of control and visibility.
2. As the name suggests, Collaboration is a 'team' effort. For Collaboration to work it requires the Host, (High Level Planning) and the Receiver(s), (Low Level Planning and Manufacturing) to talk to each other. Collaboration is not a dictation by either side, but more of a partnership.
3. Each FastReact system, Host and Receiver(s), are stand alone systems that may have other planned items, out-with the collaborated planned items, on their respective systems.

A Host system can collaborate with many Receiver systems.

### Collaborative Setup

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Collaborative Setup*

Each system, the Host and the Receiver(s), have to have their setup modified so that they can collaborate. This modification takes the form of 'Collaboration IDs'. There are several places within the set up of a FastReact system which, if the set up is for a Collaboration, need to have these IDs inputted.

**The Licence File.:** Collaboration is a Licensed option and as such must be 'turned on'. This can only be done by FastReact and will require the Loading of a new FRL Licence file. This will need to be done for all systems within the partnership.

**Collaborative Name:** The collaborative name is setup on the General Configuration dialog. This five character code will be used to identify the system.

**Routes:** Although each FastReact system can have many different Routes, the Routes which will form part of the collaboration must have a Collaboration ID. These ID numbers MUST be the same in the Host and the Receiver(s), however the names of the Routes can be different.

**Operations:** Although each FastReact system can have different Operations, the Operations which will form part of the collaboration must have a Collaboration ID. These ID numbers MUST be the same in the Host and the Receiver(s), however the names of the Operations can be different.

The Host system MUST also delegate, via options, the Operations that will be 'Delegate to the Collaborative partner'. This means that the operations with this check box marked will be 'controlled' from the Receiver(s) end.

| Host | | | | Reciever(s) | |
|---|---|---|---|---|---|
| Operation | Coll IDs | Delegate | | Operation | Coll IDs |
| Op: Issue | 10 | X | | Op: Issue | 10 |
| Op: Cut | 20 | X | | Op: Inspection | |
| Op: Embroider | | | | Op: Cut | 20 |
| Op: Sew | | | | Op: Embroider | |
| Op: Ship | 30 | X | | Op: Sew | |
| | | | | Op: Pack | |
| | | | | Op: Despatch | 30 |

#### Transport

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Collaborative Setup › Transport*

**Methods:** Although each FastReact system can have different Methods, the Methods which will form part of the collaboration must have Collaboration IDs. These ID numbers MUST be the same in the Host and the Receiver(s), however the names of the Methods can be different.

**Locations:** Although each FastReact system can have different Locations, the Locations which will form part of the collaboration must have Collaboration IDs. These ID numbers MUST be the same in the Host and the Receiver(s), however the names of the Locations can be different.

It is essential when setting up transport methodologies that the Host and the Receiver(s) 'Collaborate'. This will ensure that both systems will have the same transport times, method types and delivery dates.

**Product Types:** Although each FastReact system can have different Product Types, the Product Types which will form part of the collaboration must have Collaboration IDs. These ID numbers MUST be the same in the Host and the Receiver(s), however the names of the Product Types can be different.

**Planning Groups:** The Host

The set up of the Planning Groups on the Host system will reflect the number of Receivers. For example there may be groups dedicated solely to the Host, a China group and an Estonia group. The China and Estonia groups relate to two Receivers. These two groups will have Collaborative IDs attached to them. These Collaborative IDs MUST be different for every group within the Fast React system.

| Host | | | Remote Site 1 | |
|---|---|---|---|---|
| Group | Coll IDs | | Group | Coll IDs |
| Grp: UK | | | Grp: China | 55 |
| Grp: China | 55 | | Grp: Dc_Europe | |
| Grp: Estonia | 79 | | Grp: Bangkok | |
| Grp: UK_Finishing | | | Grp: Taiwan | |
| Grp: Sub_Con | 45 | | Grp: DC_USA | |
| Grp: UK_Man | | | | || Remote Site 2 | | | Remote Site 3 | |
|---|---|---|---|---|
| Group | Coll IDs | | Group | Coll IDs |
| Grp: Sub_Con | 45 | | Grp: Estonia | 79 |
| Grp: Printing | | | Grp: Latvia | |
| Grp: Finishing | | | Grp: Finishing | |
| Grp: Dying | | | | |

**Framework (Events):** Although each FastReact system can have many different Events, the Events which will form part of the collaboration must have a Collaboration ID. These ID numbers MUST be the same in the Host and the Receiver(s), however the names of the Events can be different.

The Host system MUST also delegate, via options, the Events that will be 'Delegate to the Collaborative partner'. This means that the Events with this check box marked will be 'controlled' from the Receiver(s) end.

| Host | | | | Reciever(s) | |
|---|---|---|---|---|---|
| Operation | Coll IDs | Delegate | | Operation | Coll IDs |
| Evt: Part I | 10 | X | | Evt: PO Confirm | 10 |
| Evt: Part II | 20 | X | | Evt: Costings | |
| Evt: Part III | | | | Evt: Order Fabrics | 20 |
| Evt: Part IV | | | | Evt: Confirm Supplier | |
| Evt: Part V | 30 | X | | Evt: Sample Approval | |
| | | | | Evt: Fabric Approval | |
| | | | | Evt: Package | 30 |

**Email Setup:** Collaborations between the Host system and the Receiver(s) system, and vice versa, are facilitated via email. Once the Licence option for Collaboration has been 'turned on' a tab called 'Collaboration' will appear on the Setup - E-mail dialog. On this tab will be set the mailbox account name of the email account associated with the FastReact particular system. The rest of the email setup is the same as normal.

**User Setup:** If the Host system has a user called 'Receiver(s)name=' then any returned updated data, notes or completed operations/events will have this user name attached to them in the Notes. For the Receiver(s) use the user name 'Hostname='.

### Planning at the Host

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Planning at the Host*

One the Host administrator and Receiver(s) administrator(s) have 'collaborated' and the separate systems have been set up so that they can 'talk' to each other. The next stage is to create and plan orders at the Host.

Creating and planning an order at the host is no different from normal order creation and planning. However, orders which are part of the collaboration process MUST be planned at High Level on the respective Group. For example, orders which will be for China MUST be planned on the China group and orders for Estonia MUST be planned on the Estonia group.

These collaboration orders only get planned at High Level.

The Host can also plan orders which will be manufactured in-house, at the Host. These orders MUST NOT be planned on any of the collaboration groups. They will be planned on the Hosts own group, in the case of the Group diagram above, this would be in either the UK, UK_Finishing or UK_Man groups. These groups will have no collaborative IDs. These non-collaborative orders can be planned at both High Level and Low Level and are controlled exclusively by the Host system.

### Sending the package from the Host

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Sending the package from the Host*

Once the orders have been planned and the Host user is satisfied that everything is in order, it is time to send the collaboration package to the respective partners.

When Collaboration is licensed two new options will appear in the Tool menu. These options, 'Send collaborative package' and 'Receive collaborative package', will be used by the Host and the Receiver(s) systems to talk to each other.

#### Send collaborative package

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Sending the package from the Host › Send collaborative package*

The first time a package is sent to a particular Receiver from the Host it will need to be configured.

**Package name:** This is the name of the package that will be sent to a particular Receiver. For simplicity the Collaboration Group name could be used.

For example China, Estonia etc.

**Description:** This optional field allows the Host user to provide a description of the package being sent.

**Select group(s) to send to remote planner:** In this section the Host user identifies the Groups that will be sent to the Receiver. This could be one or multiple groups depending upon the Receiver.

**Select a host company to receive plan changes:** This option will be left as '(none)' in the host Collaboration configuration as the Host system is not sending to another Host system.

#### Options

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Sending the package from the Host › Options*

**Hide customer details:** With this option checked the Receiver will not receive any customer details from the Host system.

**Send all orders/products:** With this option checked all orders and products on the Host system will be sent to the configured Receiver, no matter where they are planned.

**Send package to email address:** This will be the email address for the destination of this particular package. It will be the same email address that the receiving system will have configured in its email setup.

**Conformation mail email address:** This will be the email address for the destination of this particular package. It will be the same email address that the receiving system will have configured in its email setup.

**Update (button):** This will update or create a new package configuration. At the Host there may be multiple package configurations, whilst at the Receiver there may be only one configuration type.

**Delete (button):** This button will delete the current configuration.

Once the configuration of the Collaboration package has been setup it is then ready to send to the Receiver.

Click on the Collaborate tab and select Collaborate. The package will now be sent to the configured Receiver.

#### The planned orders

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Sending the package from the Host › The planned orders*

The planned orders on the High Level board which form the collaborative package will now be lock and cannot be moved, and the collaboration icon will appear on the left-hand side of the High Level board.

The planner at the Host will now be unable to move or unload the strip, change the schedule or alter the delivery date.

Locked collaborative orders are controlled via the Receiver(s). The Host can still add locked orders to Flows, change Order/Product details and amounts, and change Timetables.

### Receiving the package at the Receiver

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Receiving the package at the Receiver*

Once the orders have been sent from the Host it will appear in the Receivers email inbox, as defined on the Collaboration tab on the package configuration within the Send collaborative package menu option.

To receive the package the Receive collaborative package menu option under the Tools menus is used.

#### Receive collaborative package

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Receiving the package at the Receiver › Receive collaborative package*

This dialog will open pre-configured.

**Mail account to check:** This is the account which was setup via email under the Setup menu.

**Extract to folder:** This is the path of the folder as defined on the Import tab of the General configuration dialog.

**Check for mail:** This button will check the mailbox of the account detailed above to see if there are any waiting Collaboration packages to be processed. If there are any such packages in the mailbox they will appear in the window to the right.

**Process:** This button will import any Collaboration packages found in the mailbox. After processing, the emails will be deleted and a 'handshake' email will be sent back to the sender of the collaboration package, in this case the Host system.

By selecting the Process button the email form the Host system package will be unzipped and extracted to a local folder. It will then be imported into the Receiver system and the import files deleted from the local system and email inbox. It is upon successful import that the 'handshake' email is automatically sent back to the Host.

#### Planning at the Receiver

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Receiving the package at the Receiver › Planning at the Receiver*

The Receiver now has control of all Planning options. The orders are planned as normal on the High Level (if available) and Low Level boards.

The Receiver can alter all aspects of the collaborated information, but they are unable to delete ANY collaborated information that contains '==Hostname'. This will include:

- Orders
- Products
- Timetables
- Calendars
- Flows

The Receiver may also create orders with the postfix of '…..==Hostname'. These orders will be passed back and imported to the host system. This allows a two-way flow of information.

#### Altering Collaborated data

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Receiving the package at the Receiver › Altering Collaborated data*

At the Receiver(s), the Collaborated data is treated as local data. This means that the Receiver has 'control' of the data. The Receiver can change Order quantities, Flow schedules, Product sizes, Timetable information, etc. This allows the receiver to Plan and effectively monitor the progress of the orders.

The Receiver(s) can add notes and strip notes, which upon packaging and returning to the Host, will appear either in the Notes under the Orders dialog or on the planning board in the form of Strip Notes. The Notes data in the Host system will be prefixed with 'Receivername=' for all alterations made at the Receiver(s).

### Returning the collaborative package to the Host

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Returning the collaborative package to the Host*

> **Note:** It is NOT the order details that are sent back to the host. It is the strip details.

#### Send collaborative package

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Returning the collaborative package to the Host › Send collaborative package*

The first time a package is returned to the Host from a particular Receiver it will need to be configured.

**Package name:** This is the name of the package that will be returned to the Host. For simplicity the Receiver name post-fixed with Return could be used.

For example China Return, Estonia Return etc.

**Description:** This optional field allows the Receiver to provide a description of the package being sent back to the Host.

Select group(s) to send to remote planner

IMPORTANT: The Receiver MUST always leave ALL check boxes blank as this section is only used by the Host when sending out a collaborative package.

**Select a host company to receive plan changes:** In this option the Receiver will select a Host to which this particular package is being returned.

#### Options

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Returning the collaborative package to the Host › Options*

**Hide customer details:** With this option checked the Host will not receive any customer details from the Receivers system.

**Send all orders/products:** With this option checked all orders and products on the Receivers system will be sent to the configured Host, no matter where they are planned.

**Send package to email address:** This will be the email address for the destination of this particular package. It will be the same email address that the receiving system will have configured in its email setup.

**Conformation mail email address:** This will be the email address for the destination of this particular package. It will be the same email address that the receiving system will have configured in its email setup.

**Update (button):** This will update or create a new package configuration. At the Host there may be multiple package configurations, whilst at the Receiver there may be only one configuration type.

**Delete (button):** This button will delete the current configuration.

Once the configuration of the Collaboration package has been setup it is then ready to send back to the Host.

### Receiving the returned package at the Host

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Receiving the returned package at the Host*

Once the strip details have been sent from the Receiver it will appear in the Hosts email inbox, as defined on the Collaboration tab on the package configuration within the Send collaborative package menu option.

To receive the package the Receive collaborative package menu option under the Tools menus is used.

#### Receive collaborative package

*Context: Functionality > Planning Methodologies > Collaborative Planning › Collaborative Planning › Receiving the returned package at the Host › Receive collaborative package*

This dialog will open pre-configured.

**Mail account to check:** This is the account which was setup via email under the Setup menu.

**Extract to folder:** This is the path of the folder as defined on the Import tab of the General configuration dialog.

**Check for mail (button):** This button will check the mailbox of the account detailed above to see if there are any waiting Collaboration packages to be processed. If there are any such packages in the mailbox they will appear in the window to the right.

**Process (button):** This button will import any Collaboration packages found in the mailbox. After processing, the emails will be deleted and a 'handshake' email will be sent back to the sender of the collaboration package, in this case the Host system.

By selecting the Process button the email form the returned Receiver system package will be unzipped and extracted to a local folder. It will then be imported back into the Host system and the import files deleted from the local system and email inbox. It is upon successful import that the 'handshake' email is automatically sent back to the Receiver.

The importing of the data from the Receiver will 'over-write' the data in the Host system for all locked data which have mapped Group IDs, (see Planning Groups on page two). This Group on the High Level board on the Host system should now exactly reflect the collaborated strips on the Low Level board of the Receiver.

Things to consider when setting up a system

- Standing times
- Group properties
- Throughput times
- Efficiency profiles
- Event offsets/durations
- Section names

The above will have a baring on the information displayed at both the Receiver(s) and Host and as such, will require the Administrator/Implementer to COLLABORATE with each other so that correct information is passed between the collaborating systems.
