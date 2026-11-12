# Software Releases - 4.44

**Source:** FastReact Help (version 4.44) — Release notes (version history — what changed in which version; not how-to documentation)
**Menu path:** Software Releases > 4.44

---

Release Notes Evolve 4.44

Release Notes for FastReact Evolve version 4.44

Version Number 1.?

## Release content

*Context: Software Releases > 4.44 › Release content*

*Text extracted by OCR from the release-note pages embedded as images; screenshots inside them are omitted and minor recognition errors are possible.*

We are pleased to announce the release of FastReact Evolve & Align 4.44 to all our customers. This new release is freely available to all users with a valid support and maintenance contract. Evolve 4.44 contains a range of new features, general enhancements and fixes. You may already have an interim version containing some of these new options but may be unaware of all the extra features. This release upgrades version 4.43.

The following document aims to highlight the main changes and enhancements plus a list of resolved issues. Some of the features and functions below are licensed options so if you have any questions regarding the features and fixes detailed in this document please contact your Account Manager to arrange an overview or a detailed training session.

### New Enhancements And Additional Fucntionality

*Context: Software Releases > 4.44 › Release content › New Enhancements And Additional Fucntionality*

**Ref 17394 — New reporting function @SPLITPART to allow splitting of data in a reporting field**

Functionality has been added to allow the splitting of data in a reporting field. The @SPLITPART function can be used to split date and text fields for display in a report based upon a specified split character.

**Ref 17524 — Additional fields added to the high level and low level load lists**

The following fields are now available to be viewed in both the high level and low level load lists to assist the planner in making planning decisions:

- Order timetable
- Product work content
- Order total default work content (order quantity multiplied by the default work content)
- Order Code | Product Code | Product type Code | Customer Code | Order Required date | Order Quantity | Irder Total default work content | Order Timetable | Product Default work content

**Ref 17459 — Enhancement to low level APS to allow splitting of strips when planned late for delivery**

The low level APS engine has been enhanced to allow the splitting of a strip when planned late for delivery. The late quantity can be split and re-planned as part of the APS routine. A split threshold can be defined, in minutes, to

**Ref 17772 — Production history in the high level and low level load lists can now be viewed at the product base code level**

Users can now view production history in the high level and low level load lists at the product base code level by selecting the new drop down option in the configure area of the load list.

**Ref 17888 — New chat messages now appear as a Windows notification**

When receiving a new chat message the user will receive a Windows notification to inform they have a new message, clicking on the notification will open the ‘Chat Messages’ dialogue

- You have a new messa bh | ge

**Ref 17872 — Evolve and Align progress indicator now visible in the Windows task bar**

The progress of a task progressing in the system is now visible in the Windows task bar on the FR icon

**Ref 17399 — Product attributes are now visible in the Products>Grid Entry dialogue**

**Ref 17393 — A new option to allow ‘plan in group’ not to be sent as part of a collaboration**

**Ref 17701 — A new dashboard report setting to allow the clearing of data from today onwards from the output table before saving the report data**

**Ref 17443 — When using any of the options to manage missing orders (Setup > Configure > General > import tab) the results will now be logged as a warning in the ‘IMPWARN’ file and on the ‘Reports’ tab after importing**

**Ref 17781 — In a multi stage system the production history in the load list now shows only the history based on the planning stage of the selected load list entry.**

### Bug Fixes And Improvements To Exisiting Fucntionality

*Context: Software Releases > 4.44 › Release content › Bug Fixes And Improvements To Exisiting Fucntionality*

**Ref 17345 — APS now excludes substitution orders**

**Ref 15095 — Strip properties dialogue now has one update button**

**Ref 17501 — Strip notes are now consistent when locking / unlocking strips**

**Ref 17539 — Low level board find summary results now include made strips**

**Ref 17544 — Update to auto activity queue to only start processing next queued activity once the previous activity has completed**

**Ref 17560 — Fix to error when trying to export a report to PDF**

**Ref 17300 — In collaborative systems if the sequence of the operations are changed the sequence will still be saved when the operation is delegated**

**Ref 17525 — Operation First Updated Date and Last Updated Date are now cleared when production updates are cleared in Tools > Utilities > Verification**

**Ref 17612 — PRODOPNS file now imports with a suffix at the end of the file name**

**Ref 17700 — Strip operation reporting fields now visible when using parallel routing**

**Ref 17777 — It is now possible to populate a test database when the SQL user has a password**

**Ref 17789 — Increased performance of the pre-production planning board**

**Ref 17796 — Fix to forecast summary report to distinguish between a zero forecast and where a forecast doesn’t exist**

**Ref 17801 — Correct Plan Groups now shown when splitting the strip for the primary operation in an embellishment set up**

**Ref 17817 — Equalise order equalises within the same planning board only**

17714 | Integer overflow error updated to give a more user-friendly message

**Ref 17714 — Integer overflow error updated to give a more user-friendly message**

**Ref 17736 — Advanced strip hints average output now only considers working days**

**Ref 17761 — Continuous build up curves now calculate correctly when strips are planned in parallel**

**Ref 17925 — Using ‘Operation made per day**’ reporting field no longer forces a system shut down**

**Ref 17953 — Target dates in ‘Standing time for order’ dialogue now shows correct target date when operations are planned in parallel**

**Ref 17975 — Event late reason notes are no longer added incorrectly when updating an order**

**Ref 17977 — Audit trail now records the name of the file imported**

**Ref 17877 — The Last Update Date in production updates is now updated when production is recorded and not when the operation is marked as complete**

**Ref 17911 — Resolved high level APS refresh issue**
