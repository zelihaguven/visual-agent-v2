# Software Releases - 4.40

**Source:** FastReact Help (version 4.44) — Release notes (version history — what changed in which version; not how-to documentation)
**Menu path:** Software Releases > 4.40

---

Release Notes Evolve 4.40

Release Notes for FastReact Evolve version 4.40

Version Number 1.?

We are pleased to announce the release of FastReact Evolve & Align 4.40 to all our customers. This new release is freely available to all users with a valid support and maintenance contract. FastReact 4.39 contains a range of new features, general enhancements and fixes. You may already have an interim version containing some of these new options but may be unaware of all of the extra features. This release upgrades version 4.39.

The following document aims to highlight the main changes and enhancements plus a list of resolved issues. Some of the features and functions below are licenced options so if you have any questions regarding the features and fixes detailed in this document please contact your Account Manager to arrange an overview or a detailed training session.

## Release content

*Context: Software Releases > 4.40 › Release content*

*Text extracted by OCR from the release-note pages embedded as images; screenshots inside them are omitted and minor recognition errors are possible.*

Below Bug Fixes Within 4.4000.6000.7

- **Bug Fix:** A plan row error is occurring in reports.
- **Bug Fix:** Various columns require adjusting in width.
- **Bug Fix:** The licence option "allow orders to be split across planning boards' is turned off, but you can still transfer orders to different planning boards.
- **Bug Fix:** There is an auto size issue in advanced strip hints.
- **Bug Fix:** Order Work Content updating at remote site with warning “Updating order work content, order not found”.
- **Bug Fix:** Range check error when logging into the database as the # user.
- **Bug Fix:** Duplicate strips in the STRIP_DATA table for 18 Orders.
- **Bug Fix:** A system with 1 planning board can activate the deallocate order button.
- **Bug Fix:** MRP does not calculate orders in the low level load list even when planned at high level.
- **Bug Fix:** An order should be shown in the sewing planning board low list, but when a search for the order is done, there are several strips for the order, but the sewing strip cannot be found.
- **Bug Fix:** If you delete an operation, then try to do anything else on the system it crashes and you cant log back in.
- **Bug Fix:** The delete function is not working as it does not delete the package after clicking the delete button.
- **Bug Fix:** A DashBoard export reports from Evolve fails due to date formats.
- **Bug Fix:** R.ROW_CON_USG_ and S.CONSTRAINT_TARGET_AMOUNT reporting fields to calculate using remaining order size quantity rather than the original size ratio.
- **Bug Fix:** Small balances of the HOST order remain in the LLPB, after Creating and substituting orders from Bulk order sizes.
- **Bug Fix:** Changes to the planning row capacity does not refresh for multiple users.
- **Bug Fix:** An error message is occurring when creating a What-if database.

New Enhancements Within 4.4000.6000.7

- **Enhancement:** A new function has been added to allow the sort function to work between locked strips.
- **Enhancement:** When creating a test database, you can now convert a restored database to be the test database.

4.39 Sprint D Below Bug Fixes Within 4.3900.11700.22

- ._ | The sewing quantity becomes less than the order quantity after a transfer production Bug Fix iq update is performed.
- **Bug Fix:** When searching using ‘Problems - Late events’ in correct results returned.
- **Bug Fix:** Changes to the planning row capacity do not refresh to multiple users.
- **Bug Fix:** Maintenance function to 'clear production updates' does not clear rejects.
- **Bug Fix:** Target dates for “Cut Start” Event is showing in 15/03/2017 but the event and Order were 9 all completed in Oct 2016.
- **Bug Fix:** Product event is not skip when enter '0' from multiple updates dialog.
- **Bug Fix:** Making next routes, current routes on startup fails.
- **Bug Fix:** The Plan Row Capacity and Available Capacity Fields have the same results.
- **Bug Fix:** Numeric Schedule Override qty column using incorrect value for time.
- bua rik Audit log txt file went to FR_Program folder instead of the one define in FR in version 9 FastReact_4_3900_8800_14.
- New Enhancements Within 4.3900.11700.22
- **Enhancement:** New additions have been added to Low Level APS.
- **Enhancement:** A pop out hint box has been added to display long order names.
- **Enhancement:** New additions have been added to the pop out display.
- **Enhancement:** A new feature has been added to allow the moving of strips to a specific row on the low level planning board.
- **Enhancement:** The ability to define the days period on a learning curve by learning curve basis.
- **Enhancement:** odifica lonito allo e allo ° A modification to allow the ‘allow work content override’ function to create or remove strips.
- **Enhancement:** ] ire" modification has been added so that you can set a host order from the load
- 4.39 Sprint C Below Bug Fixes Within 4.3900.8800.14
- **Bug Fix:** The average efficiency scoring is using the full capacity for a partially loaded final day.
- When AHOS is licensed as “standard” (spread quantity across strips each day) it's not Bug Fix| taking into account already substituted quantity resulting in it substituting into already fully substituted strips.
- **Bug Fix:** An access violation error message is appearing if the customer field has not been entered 9 in order items.
- **Bug Fix:** When in pre-production planning, the parent line expected date does not update when a 9 child line has been deleted.
- **Bug Fix:** An export report is no longer running.
- **Bug Fix:** When importing multiple dates for production in a UPDNORNM file. An error is occurring.
- **Bug Fix:** If a user needs to change the line area width so that you can view it in the low level 9 planning board, a range check error occurs.
- .. | The order items are available to be translated but do not get translated in the system once Bug Fix : they have been applied.
- **Bug Fix:** The forecasting dialogue is accessible even though it is not licenced in the system.
- **Bug Fix:** When trying to receive a collaboration package an error message is occurring.
- **Bug Fix:** Plan row constraint load reporting is not reporting the correct load.
- **Bug Fix:** If | import a production update for an order that does not exist In FastReact, an error 9 message is shown.
- ._ | The function to overwrite working days only when changing the calendar dates is not Bug Fix : working correctly and not updating.
- ._ | The function to attach continuous learning curves is not working when the time on the day Bug Fix . of the change over is less than normal.
- **Bug Fix:** When you run a batch scheduled report, an error message is being generated.
- New Enhancements Within 4.3900.8800.14
- **Enhancement:** ] 4 new option has been added so that you can print out the products and orders grid style screen.
- **Enhancement:** Anew modification has been added to allow users to be able to adjust the size of the acceptance list window.
- **Enhancement:** base code+code part 2. A new modification has been added so your have the ability to use push/pull for
- **Enhancement:** p et roaiication has been added to allow you to import the order operation group
- **Enhancement:** ere erpancement will allow for any changeover allowance to be visible as load on
- 4.39 Sprint B Below Bug Fixes Within 4.3900.6000.12
- **Bug Fix:** When using the auto load function on the load list, not all of the orders with property 9 match were getting loaded onto the board but are remaining in the load list.
- **Bug Fix:** When in grid entry and you create a new line, if you click on another order name, this 9 causes an error that forces FastReact to close.
- **Bug Fix:** Archived orders are loaded into the cache when logging into FastReact.
- **Bug Fix:** Regarding the advanced strip hints function, the overall efficiency is incorrect and it is 9 caused by the strip length round off.
- .. |The customer, customer reference and customer style searches do not get remembered in Bug Fix the system
- **Bug Fix:** an error message is being displayed when checking the range validation in the customer window.
- A locked strip next to a non locked strip are considered as matching which should no be Bug Fix the case. If the 1st strip of a consolidation is locked, the whole consolidation is drawn as 9 locked. It can still be picked up (as long as the 1st strip isn't clicked), but, the moving strip isn't drawn.
- **Bug Fix:** Pulling orders/strips forward to align to the production end is taking a long to align.
- **Bug Fix:** If a strip has been locked and you select the peek function and then hover over the locked 9 strip. Nothing is displayed in the peek window.
- **Bug Fix:** The enable grid data entry option should be disabled, but it is not disabled.
- .. |When a strip has been locked on the planning board, even though it has been locked, you Bug Fix : : are still able to move the strip.
- **Bug Fix:** Unable to open the Planning board after upgrade and SQL conversion from Access.
- **Bug Fix:** Changes to Winding/Weaving planning boards regarding adding in new strips are not being saved.

New Enhancements Within 4.3900.6000.12

- **Enhancement:** The hourly planning calculation total is now a decimal, with the cumulative value being rounded up.
- **Enhancement:** The grid entry screen must now allow the creating, updating and deleting of basic orders and products.
- **Enhancement:** A new option 'Whole/complete values' have been added in to the fields in the report layout, and is only enabled for repeating fields.
