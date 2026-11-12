# Software Releases - 4.37

**Source:** FastReact Help (version 4.44) — Release notes (version history — what changed in which version; not how-to documentation)
**Menu path:** Software Releases > 4.37

---

Release Notes Evolve 4.37

Release Notes for FastReact Evolve version 4.37

Version Number 1.0

## Introduction

*Context: Software Releases > 4.37 › Introduction*

We are pleased to announce the release of FastReact Evolve & Align 4.37 to all our customers. This new release is freely available to all users with a valid support and maintenance contract. Evolve 4.37 contains a range of new features, general enhancements and fixes. You may already have an interim version containing some of these new options but may be unaware of all of the extra features. This release upgrades version 4.36.

The following document aims to highlight the main changes and enhancements plus a list of resolved issues. Some of the features and functions below are licenced options so if you have any questions regarding the features and fixes detailed in this document please contact your Account Manager to arrange an overview or a detailed training session.

## Release content

*Context: Software Releases > 4.37 › Release content*

*Text extracted by OCR from the release-note pages embedded as images; screenshots inside them are omitted and minor recognition errors are possible.*

4.37 Sprint A New Enhancements within 4.3700.2200.4

- **Enhancements:** Working hour update issue in Calendar.
- **Enhancements:** Adding new subtotal option “Count Distinct NZ” which ignores null(blank) cell.

Enhancement 1: Working hours issue in calendar.

When you go to setup, general, calendars. In the holidays tab when you select the calendar and then change the working hours to have less than what they usually have, that week now goes yellow instead of blue.

Enhancement 2: Adding new subtotal option “Count Distinct NZ” which ignores null(blank) cell

If you load up a report and go to the layout screen, if cell has a subtotal enabled you can change it to count distinct NZ. Below bug fixes within 4.3700.2200.4

- **Normal Bug:** Customer UDF could be updated by certain users even the security group right set for it is View Only.
- **Normal Bug:** Do not send Handshake if any import errors or failures occur.
- **Major Bug:** Service user shutdown automatically during saving the plan for variant reporting.
- **Normal Bug:** MRP calculation doesn't take into account the process group overridden at Order level.
- **Major Bug:** Text background colouring doesn't work for Events rotation.

4.36 Sprint F New Enhancements within 4.3600.9900.22

- **Enhancements:** Materials with no demand option does not work in MRP by Order loop.
- **Enhancements:** Filter LLPB Planned Schedule by Stage.
- **Enhancements:** SCS-Over-ride_Import_Folder - strategic Usability.

Enhancement 1:Materials with no demand option does not work in MRP by Order loop. Materials with no demand can now be seen.

Enhancement 2:Filter LLPB Planned Schedule by Stage.

You will be able to select the stage only when you have 2 planned operation in the same section. To change the stage you will need to right click on a strip and go to planned schedule. Then there is a drop down box that says stage. Here then you can change the stage(planned operations)that you will see data for.

Enhancement 3:SCS-Over-ride_Import_Folder - strategic Usability.

- Add field headers from separate header file A Use compliant import file field names Allow import of data from multiple files Strip surplus quote delimiters from tab separated data Skip change log mechanism for faster imports Enable scheduled importing of data Do not E-Mail successful imports Log successful imports to text file Retain import files (timestamp) after all imports Use export encoding when importing Convert ANSI files to UTF-8 HOTFIX: Reset buffer for each line read. Only use if odd characters are mis-transl: Use automatic importing when files are changed © Allow import file location to be overridden locally ¥

To enable this option you will need to go to setup, configure, general. Go to the import data tab, and on the left is an options box, scroll down until you find the option ‘allow import file location to be overwritten locally’.

Below bug fixes within 4.3600.9900.22

- **Normal Bug:** Expedite issues aren't being highlighted in pooled MRP when the delivery is coming into the second location.
- **Normal Bug:** Order set hard coded to 30 characters.
- **Normal Bug:** Existing order will be deleted if import Orders file without DQ:1 column.
- **Minor Bug:** Invalid WIP warning.
- **Normal Bug:** Production Update Utility looks at a separate flag for marking operations as complete.
- **Normal Bug:** Override customer profile option Unticked cannot be saved.
- **Minor Bug:** Copy function in Product type causes an error and forces to close the system.
- **Normal Bug:** Expedite issues aren't being highlighted in pooled MRP when the delivery is coming into the second location.
- **Normal Bug:** Running a “Materials (MRP) by order” report that requires MRP to be recalculated causes the report to fail.

New Enhancements within 4.3600.8500.17

- **Enhancements:** New flow rotation where only strips on and after the date of the first issue are to be coloured red.
- **Enhancements:** Add a flow variance bar to the top of the low level planning board.
- **Enhancements:** SCS_Highlight rejected orders when loading orders from HL load list.

Enhancement 1:New flow rotation where only strips on and after the date of the first issue are to be coloured red.

To enable the flow rotation you need to go to setup, configure, planning, then the rotation tab. When you create a rotation the option to have the flow colours is under strip colours. Drop this down and at the bottom wil be flow variance(see image). When you add in the rotation and go to the flow rotation in the low level plan this is an example as to what it will look like.

Enhancement 2:Add a flow variance bar to the top of the low level planning board.

Wed 02/03/2022 19:42:00 720.0 x 16:00 x 100% = 11520.000

WB + Trp Line 02 1,200 4

GD) + Trp Line 03 1,200 1

The enable to flow variance bar you will need to click on the eye icon(see image) this will add in the flow variance bar shown in the image above. When you hover over a strip it will appear in that bar showing the whole strip.

Enhancement 3:SCS_Highlight rejected orders when loading orders from HL load list. Rejected orders are now highlighted differently if they are selected. The colour used is a mixture of the 'Red', non-selected, colour and the highlight colour of the current system. This is a purple colour on standard systems but will varying depending on Windows themes used. Below bug fixes within 4.3600.8500.17

- **Normal Bug:** PED for an order showing up wrong in the report.
- **Normal Bug:** There is system warning when right click the “Consolidate progress” against the order in LL planning board.
- **Normal Bug:** # log in planning board Eco Smart with “no valid group/sections...”.
- **Major Bug:** Order entry grid right click functionality not picking up the correct Order.
- **Normal Bug:** Sort by Delivery Date is not working on LL board.
- **Normal Bug:** Issues toggling between different numeric schedules while “strip peek” is on.

4.36 Sprint D New Enhancements within 4.3600.7000.13

- **Enhancements:** Fade out non-matching flow variance & production schedules after a find (LLPB Drop down).

Enhancement 1:Fade out non-matching flow variance & production schedules after a find (LLPB Drop down). a d ? x

Fields in bold below will accept 4 wild card find Order set ill Row name test al Product iv] 1 Operation work content ml

Customer ill Product description

In bill of material [v] Transit Transport method ww]

Show orders starting between

- Find orders where production has started Find orders where production has not started Find orders with parallel processes
- = Report * Clear all settings

This is a license option so will need to be enabled to do this. To fade out order that do not match the flow variance, you need to find an order. So go to the find icon, and on the right there is a drop down box which says flow name (see image), you can then select the flow filter that you want to use, then click find. The orders with that filter will be visible but the orders without the filter will be faded out as shown in the image above.

Below bug fixes within 4.3600.7000.13

- **Normal Bug:** Range check error with PRODUCT_EVENTS.SAVED_VARIANCE.
- **Normal Bug:** The Group Loading for a Group does not report the same as the Strip loading for that same Group.
- **Normal Bug:** Add increase order quantities to existing Low level strips not working.
- **Normal Bug:** Changing standing time using Multiple Updates does not actually do anything.
- **Normal Bug:** Event complete date changes daily.
- **Normal Bug:** Semi-Auto Planning results in multiple strips being picked up after loading.
- **Normal Bug:** Material rotation no longer available in HL and LL Planning boards.
- **Normal Bug:** Production Updates (now and again) can't find strips to update.
- **Major Bug:** Incorrect MRP calculation when using host order functionality.

4.36 Sprint C New Enhancements within 4.3600.5500.8

- **Enhancements:** Modification to allow successful import emails for collaboration packages to include collaborative name.

Enhancement 1:Modification to allow successful import emails for collaboration packages to include collaborative name. The package will have the collaborative ID as part of the emails. Below bug fixes within 4.3600.5500.8

- **Normal Bug:** Process With - Unable to split strips.
- **Normal Bug:** Read only user can create batches.
- **Normal Bug:** Embellishment doesn't kick in when using the ‘Selected Strips' right click option to move multiple strips on the HLPB.
- **Normal Bug:** HL Sort always displays critical path events.
- **Normal Bug:** HL Sort Strips: 'Show Primary Operations (strips) sorted by stage sequence' stops you from viewing the strips.
- **Normal Bug:** Plan Row: Notes does not work in report.
- **Normal Bug:** Two digit year causing error creating date validation.
- **Major Bug:** Operations out of sequence.
- **Normal Bug:** In collaborative system with company suffix enable, PPPB filtering not working.
- **Normal Bug:** CalcFlowVariance Error when loading an order not attached to a flow.

4.36 Sprint B

New Enhancements within 4.3600.4200.5

- **Enhancements:** Multi-Pack Linking Strategic (formally: Modification to allow orders with the same packing code to be visualise and end at the same time).

Enhancement 1:Multi-Pack Linking Strategic (formally: Modification to allow orders with the same packing code to be visualise and

end at the same time).

Time fence days it} Strip hints

Equalise order multiplier 1 8 ¥

a | Product description Options User defined strip display Show row capacity factor x calendar hours x capacity A © Strip notes Show "Last product type" indicator on low level rows Order notes Do not calculate Total Days Early for each row (speeds up loading) Product notes Hide Confitmed orders in Low Level load list and order accept option | Contract Quantity M Hide Provisional orders in Low Level load list and order accept option Deliver to Y. V Hide Speculative orders in Low Level load list and order accept option M Hide Transit orders in Low Level load list and order accept option SOTA Hide MPS Suggested orders in Low Level load list and order accept optic Strip highlighting M Use Grid style load list (J Orders [Deliveries Use prep start calendar Allow load list to be constantly open when planning LJ Products [User defined Enable product type efficiency warnings [_] Product types M Pull # Push order by production end (defaults to production start) [1 Customers Realign strips to production date after production update Z Enable qroup/efficiency profiles Order optimise loading Product optimise loading © Enable work in progress monitoring @ Disabled @ Disabled Planner cannot change Standing time for normal operations : : High Level planner cannot change Planning board for order O Waining only O Waining only Allow orders to be split across planning boards < s White out none matched strips planned from load list © Prevent loading O Prevent loading

Operation move time by Product (defaults to Orders) Show product description on load list [defaults to Order)

ee Specify quantity to split

© Events report @ Update Progress

=| Consolidated progress

= Linked order relationships @ Change start up Change standing time @ Order details

& Order flows

‘= Edit capacity options ‘© Change working hours Multiple strip options

To make orders that are the same but are on different rows have the same end date you need to change a setting before you push/pull the order. So if you go to setup, configure, planning. in the configure screen in the options box shows in the image above there is a tick option which says 'push/pull order by production end (defaults to production start). Enable this option then click update. Now if you go to your low level plan and right click on s strip and go to push/pull order, order, as shown in the image above, you can move all the strips to end on the same day(seen in the image above)

Below bug fixes within 4.3600.4200.5

- **Normal Bug:** FR Remote: Not enough storage is available to complete this operation.
- **Normal Bug:** DB access components error in FR4.
- **Normal Bug:** ‘Strip not created! error.
- **Normal Bug:** Function “Sort row based on selection” not available after Evolve 4.34.
- **Normal Bug:** Batch tickets rounding down.
- **Normal Bug:** Material colour display incorrect.
- **Normal Bug:** Numeric Loading value does not match the Report or manual calculation.
