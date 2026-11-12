# Software Releases - 4.41

**Source:** FastReact Help (version 4.44) — Release notes (version history — what changed in which version; not how-to documentation)
**Menu path:** Software Releases > 4.41

---

Release Notes Evolve 4.41

Release Notes for FastReact Evolve version 4.41

Version Number 1.?

We are pleased to announce the release of FastReact Evolve & Align 4.41 to all our customers. This new release is freely available to all users with a valid support and maintenance contract. FastReact 4.40 contains a range of new features, general enhancements and fixes. You may already have an interim version containing some of these new options but may be unaware of all of the extra features. This release upgrades version 4.40 .

The following document aims to highlight the main changes and enhancements plus a list of resolved issues. Some of the features and functions below are licenced options so if you have any questions regarding the features and fixes detailed in this document please contact your Account Manager to arrange an overview or a detailed training session.

## Release content

*Context: Software Releases > 4.41 › Release content*

*Text extracted by OCR from the release-note pages embedded as images; screenshots inside them are omitted and minor recognition errors are possible.*

Below Bug Fix Within 4.4100.5501.1

- **Bug Fix:** Various fixes for order level work content overrides. * $ bug 16174

Below Bug Fixes Within 4.4100.5500.6

- **Bug Fix:** The hint text for move to delivery date does not give a clear explanation of the function of the key combinations. * #* bug 15733
- **Bug Fix:** Selecting strips with row drop down does not turn strips black. * #*bug 15776
- **Bug Fix:** Multi select orders with the row drop down clears the row. * #* bug 15779
- **Bug Fix:** Unable to find the orders through the find function when orders are in the HL load list. * #* bug 15791
- **Bug Fix:** Stop the system from referring to the distributed users if the license option is turned off. * #*bug 15803
- **Bug Fix:** The ‘default’ naming can be changed when defining the change allowances. * #*bug 15855
- **Bug Fix:** The fix of calculating the build up efficiency based on average calendar hours to be made a switch. * # bug 15881
- **Bug Fix:** The Pull Forward Is not moving strips when the locked strip functionality is deployed. * #*bug 15884
- **Bug Fix:** When using the plan score, once it has finished incorrect results are being shown. * ¥§ bug 15897
- **Bug Fix:** Grid Entry slowness after login in to system with user accounts. * #*bug 15937
- **Bug Fix:** The MRP results are not being calculated as the strips on the planning board are still appearing as grey. * #* bug 16088
- **Bug Fix:** Embellishment operations are not getting calculated according to the route. * #* bug 16112

New Enhancements Within 4.4100.5500.6

- General Enhancement | Add “Work Time Type” concept to production updates and Attended Time logging. * #bug 14680

To be able to use this option you will need to have enabled the ' Use work time type' option in the licence file. Once this option has been enabled you are able to create and maintain the work time types. To do this you will need to click on setup-production-Work time types.

Work time type can also be recorded against the order progress. To do this right click on an order on the low level planning board and select update progress.

When the screen loads, towards the top right hand corner, there is the option for the work time type which you can then select.

- General Enhancement | Tool To Assist In the Logging of Issues When the Service User logs off. * #* bug 15613
- General Enhancement | Amend strip flow colours to reflect both negative and positive flow variance. * # bug 15864

4.40 Sprint C Below Bug Fixes Within 4.4000.11000.19

- **Bug Fix:** Upgrading to 4.4000.6001.1 loses the “Transfer to another planning board” option from the load list. * #*bug 15563
- **Bug Fix:** Update function disabled for future dates when adjusting within an existing time period. * #*bug 15615
- **Bug Fix:** When using the option 'save dates in exported format' it only applies to the actual data in the reports and not the headers. * bug 15638
- **Bug Fix:** Critical event tick is not retained on the collaborated order events when the timetable is updated. * #bug 15639
- **Bug Fix:** Users can update the 'Change availability’ dates even though they do not have security access. * #bug 15668
- **Bug Fix:** Bucket capacity not redrawing when strip length changed, until moved away and re-planned. * #*bug 15677
- **Bug Fix:** Clicking on the Score button on the LL Planning Board produces an Access Violation error. * #*bug 15684
- **Bug Fix:** Days late scoring showing less late orders than there are in the whole system. * #*bug 15685
- **Bug Fix:** Turning off an order level work content override with production only checks applied production updates. * #* bug 15687
- **Bug Fix:** The ‘complete all fastreact orders missing from the import file' does not work. * # bug 15708
- **Bug Fix:** Multiple deliveries are imported even though the license limit is just 1. * % bug 15749
- **Bug Fix:** Users without rights are able to edit and save the planning board. * #*bug 15829

New Enhancements Within 4.4000.11000.19

- General Enhancement | Display percentage of ‘separate load’ for high level buckets. * #* bug 15576

To see this new option on the high level planning board you will need to enable the option ' Use expanded mode' The location of this option is as follows. (Setup > Configure > Planning > High Level (tab) > Options > Use expanded mode) Then in the high level planning board when you hover over a bucket you will see that the percentage is now shown twice. Depending on the bucket you hover over, the percentage will be different as this will be the percentage of a separate load.

4.40 Sprint B

Below Bug Fixes Within 4.4000.8400.16

- **Bug Fix:** MRP for systems with “Issue to Order Groups” licence enabled gives incorrect MRP after WIP updates. * #*bug 15351
- **Bug Fix:** Two users are able to log into the planning board at the same time, and both have access to change/update the board. * bug 15392
- **Bug Fix:** Search function not jumping to strip when using 2 planned ops on different boards. * #*bug 15400
- **Bug Fix:** Error when loading a strip at high level that has previously been planned at low level. * #* bug 15537
- **Bug Fix:** Warning pop up when saving the Grid Entry in collaborative system remote site. * #*bug 15606
- **Bug Fix:** Operation sequence incorrect when using product routing for embellishment planning with more than 100 non-planned operations. * #* bug 15630
- **Bug Fix:** Move order to delivery date not work properly. * ¥ bug 15397

New Enhancements Within 4.4000.8400.16

- General Enhancement | The ability to copy down in the HL strip numeric display. * #* bug 14775

You are now able to copy within the numeric schedule. To do this you will need to go to the high level planning board and find an order that has not been planned at low level. Right click on the strip and select the option numeric schedule.

In the override qty column you can change the qty where the data is already filled in

**Ref 1105 — /2022 (Wed) | 8.00 | 290**

- Date | Hours | Original qty | Override qty

Now if you click on the top line and click on the fill down button.

The other quantities will have been updated as well as a new quantity to hold the quantity that you changed on the above lines

- Date | Hours | Original qty | Override qty
