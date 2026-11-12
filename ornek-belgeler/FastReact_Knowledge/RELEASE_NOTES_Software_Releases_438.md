# Software Releases - 4.38

**Source:** FastReact Help (version 4.44) — Release notes (version history — what changed in which version; not how-to documentation)
**Menu path:** Software Releases > 4.38

---

Release Notes Evolve 4.38

Release Notes for FastReact Evolve version 4.38

Version Number 1.0

## Introduction

*Context: Software Releases > 4.38 › Introduction*

We are pleased to announce the release of FastReact Evolve & Align 4.38 to all our customers. This new release is freely available to all users with a valid support and maintenance contract. Evolve 4.38 contains a range of new features, general enhancements and fixes. You may already have an interim version containing some of these new options but may be unaware of all of the extra features. This release upgrades version 4.37.

The following document aims to highlight the main changes and enhancements plus a list of resolved issues. Some of the features and functions below are licenced options so if you have any questions regarding the features and fixes detailed in this document please contact your Account Manager to arrange an overview or a detailed training session.

## Release content

*Context: Software Releases > 4.38 › Release content*

*Text extracted by OCR from the release-note pages embedded as images; screenshots inside them are omitted and minor recognition errors are possible.*

New Enhancements Within 4.3800.1701.3

- **New Feature:** Low Level APS.
- **Enhancement:** Allow Lookup Lists used in Import Pre Processing to be stored and maintained.
- **Enhancement:** Support for .png, .bmp image formats.
- **Enhancement:** Modification to allow 'order work content override’ to be collaborated from host site to remote site.
- **Enhancement:** The ability to define financial values up to 6.
- **Enhancement:** Increase field size for delivery location.

New Feature 1: low Level APS

Low Level APS allows users to schedule and reschedule the orders on the planning board according to a large range of priority criteria. The rules for planned resource selection (sewing team, knitting machine etc) are completely configurable by the user and can include a stacked list of descending rules. Users can configure multiple different planning policies which follow different prioritisation criteria for the orders and selection criteria for the selected resource (team / machine). The different policies can be run back to back with a comparative score being generated for each policy. A typical factory with 2000 — 5000 live orders and 100 sewing teams may take just a few minutes to plan and re-plan to different policies — a task that would normally take a planner several days. Management time and focus is freed up to concentrate on decision making to achieve the highest productivity and maximise on time delivery (or any other criteria deemed to be essential) based on accurate planning information rather than hunting around for days for the information to be generated manually - which may well be out of date by the time it has been evaluated anyway.

If you are interested in this functionality please contact your FastReact Account Manager.

Enhancement 1: Allow Lookup Lists used in Import Pre Processing to be stored and maintained within the software.

Pre processing lookup lists can now be held and maintained from within Evolve rather than from within the pre processing instruction files. This option must be enabled in the licence file.

Enhancement 2: Support for.png, .bmp image format.

A modification to support bitmaps has been included.

Enhancement 3: Modification to allow ‘order work content override’ to be collaborated from host site to remote site.

Only applicable for systems where work content override(WCO's) at order level is enabled. Work content by override is now collaborated between systems.

1. WCOs will be collaborated from the site that owns an order to the other sites.

Enhancement 4: The ability to define financial values up to 6

This modification applies to both order and product financial values. the number of decimal places can be defined up to a maximum of 6. Enhancement 5: Increase field size for delivery location. The delivery location field size has now been updated to 25 characters. Below Bug Fixes Within 4.3800.1701.3

- **Normal Bug:** Material Supply rotation does not work.
- **Normal Bug:** Range check error when clicking customers in customer profiles.
- **Normal Bug:** Import pre-processing does not recognise new Unicode formats available in std import.
- **Normal Bug:** Semi auto plan row error when moved the position.
- **Normal Bug:** Product event notes not reporting when “include dev events in order based reports”.
- **Normal Bug:** Issued MRP colour not correct in Material Query screen.
- **Normal Bug:** FRPRODUPDATE: Completion Flags get cleared when refreshing the planning board.
- **Normal Bug:** Deleting a single failed event note clears all the failure notes from the notes dialog.
- **Normal Bug:** The report showing incorrect Production end time.
- **Normal Bug:** Automatic Host Order Substitution Error.
- **Major Bug:** Can't use keyboard shortcuts to change the embellishment schedule.
- **Normal Bug:** Unable to Import Products File.

New Enhancements Within 4.3700.7600.10

- **Enhancements:** Ability to automatically create an ORDUPDAT file when an error is created on import.

Enhancement 1: The ability to automatically create correction files for re importing data where errors are detected.

The ability to automatically create files for data correction and re importing where data integrity issues or other import problems have been countered during initial import.

The option “Enable import file errors to generate export files” has been added to the system. Enabled under the FRS log on, this option will display a “Configure import file errors” button under Import Data. This button will allow the user to enable various import files and define what errors match. When an import error matches one of the defined errors a matching export file will be created.

Please contact your FastReact Account Manager for more information on this functionality.

- Import File Errors x
- An <empty> value for "Matching Error® will match ALL errors.

Below Bug Fixes Within 4.3700.7600.10

- **Normal Bug:** The MRP material detail loop is showing a different Issued gty than everywhere else in the system.
- **Normal Bug:** Need to increase the material limit in the BOM.
- **Normal Bug:** Products grid entry allows a production timetable to be selected.
- **Major Bug:** Order level material reservations aren't collaborated.

New Enhancements Within 4.3700.6200.9

- **Enhancement:** Report generation is slow.

Enhancement 1: Report generation has been improved for faster generation of reports, by changing the routine to not open the table in “locate” mode and to work top to bottom through the data. Below Bug Fixes Within 4.3700.6200.9

- **Normal Bug:** Importing in Activity scheduler pops up an error.
- **Normal Bug:** Critical event not flag after collaboration to the remote site.
- **Normal Bug:** Integer overflow calculating high-level quantity of a strip.
- **Major Bug:** Access violation causes system down.

No New Enhancements Within 4.3700.4700.7 Below Bug Fixes Within 4.3700.4700.7

- **Normal Bug:** Order cannot prevent to plan in the Group/row after setup Customer profile under Auto Plan Group/row.
- **Normal Bug:** Order Items: Free-typed text fields display garbage.
- **Normal Bug:** Order Items: Access Violation when trying to open the dialog.
- **Normal Bug:** The grid entry takes a lot of time to save the data entered.
- **Normal Bug:** Header files not being saved to configuration archive.
- **Normal Bug:** Access Violation saving forward plan.
- **Normal Bug:** Error importing UPDNOR\M file.

No New Enhancements Within 4.3700.3400.5 Below Bug Fixes Within 4.3700.3400.5

- **Normal Bug:** Collaboration: Normal TXT import files being imported during collaboration import.
- **Normal Bug:** Collaborative: Failed collab imports with a Timestamp do not get reimported.
- **Normal Bug:** Client Regina suffer auto export report issue with error “Invalid floating point” and “Integer overflow’.
