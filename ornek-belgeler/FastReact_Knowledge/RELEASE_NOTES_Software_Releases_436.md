# Software Releases - 4.36

**Source:** FastReact Help (version 4.44) — Release notes (version history — what changed in which version; not how-to documentation)
**Menu path:** Software Releases > 4.36

---

Release Notes Evolve 4.36

Release Notes for FastReact Evolve version 4.36

Version Number 1.0

## Release content

*Context: Software Releases > 4.36 › Release content*

*Text extracted by OCR from the release-note pages embedded as images; screenshots inside them are omitted and minor recognition errors are possible.*

We are pleased to announce the release of FastReact Evolve & Align 4.36 to all our customers. This new release is freely available to all users with a valid support and maintenance contract. Evolve 4.36 contains a range of new features, general enhancements and fixes. You may already have an interim version containing some of these new options but may be unaware of all of the extra features. This release upgrades version 4.35.

The following document aims to highlight the main changes and enhancements plus a list of resolved issues. Some of the features and functions below are licenced options so if you have any questions regarding the features and fixes detailed in this document please contact your Account Manager to arrange an overview or a detailed training session.

Modifications: New Functionality

A. with the option Ignore sizes on MRP calculations

This functionality will show the quantity that can be made based upon the MRP calculation and the Order quantity.

On the current Materials display, FR will calculate the quantity that can be made by subtracting the nonproduceable from the order quantity and display as per the above screen shot. The items to be displayed are:

- The Producable (min)
- The Non-Producable (max)
- The Non-Produceable

Prevent Loading by Customer in Groups/Rows

A new option Enable group/customer profiles has been added to Setup - Configure - Planning - Configure (tab) under Options.

A new menu Customer profiles has been added to Setup - Production. From here you can manage customer profiles.

A new field Customer profile has been added to Setup - Planning - Plan Groups - Define (tab) under Properties and Setup - Planning - Plan Rows - Define (tab) under Properties.

A new field Override customer profile has been added to Orders - Add/Amend - Define (tab) under Planning. If checked the specified order will ignore the customer profile define on a Group/Row.

New fields Customer match (group) & Customer match (row) have been added to the Strips/Strip Plan by Day report loop under the Strip field group - please note that these fields will return 0 (no match), 1 (match) or n/a (not planned at this level) if the strip's order's Customer is not valid for the Customer Profile defined on the planned group/row (irrespective of the value of the override customer profile of the order).

A new import file CUSTPROF has been added. This can be used to manage Customer Profiles. CP.NAME - profile name CP.NEWNAME - new profile name (optional), if being renamed CP.DELETE - delete profile (optional) CP.CUST - customer name (optional) CP.ENABLED - whether customer is enabled (optional) ls

Efficiency Warnings by Product Type

The option Enable product type efficiency warnings has been added to Setup - Configure - Planning - Configure (tab) - Options. If ticked the system level efficiency warning will be hidden and the efficiency warning will be at Product Type level.

The rest of the system operates as before, however the value used to see if a warning should be displayed is based on the Product Type rather than the system.

NB. If using the Product Type, the product type will be included within the warning message (Production efficiency is below acceptable limit : product type).

Modifications: Enhancements to existing functionality

FastReact Evolve and Align now has encryption options (none, SSL & TLS) for POP3 to both the Setup - Email - General (tab) and Setup - Email - Collaboration (tab) if applicable.

These new authentication settings allow the Fast React Products to work with Office365.

Reporting

The Event field 'Event external reference’ can now be used in the filtering of data in the report.

This allows the user to have multiple filters on a field without breaking the 50 character limit: Include list (‘Red diamond' icon)

- List can include spaces and square brackets - allows for partial matches (e.g. a filter of “400

Not Include list (‘Crossed out diamond’ icon)

Exact Include list (‘Green equals’ icon)

- List MUST be separated with square brackets - allows for only exact matches (e.g. a filter of

Toggle switch for Material Name and Description on the Materials tab of Orders and Products

The Materials tab on both the Order & Product screens now has an option to Display material descriptions (if available).

If ticked, the various parts of the tab will display the relevant material description rather than the material name, if there is a description against that material.

he General | tip Financial | i Sizes | & Planning Ja) Materials a Operations | iC] Events | SS User values | SB Forecasting

Category (optional) Specification

FB.561.123.334 Display material descriptions {if available)

FB.977.980,231 Duplicated category/specification pairs will not be saved FB_Generic 34598 FB_Generic_9934

Limit view of Product and Order UDFs based on Customer

It is now possible to configure which UDFs will be visible for a Customer.

Within the Customers - Add/Amend dialog there is a tab called User defined fields. On this tab it is possible to select a Customer and a UDF type. Once these are selected, a list of currently visible UDFs is shown along with any other available UDFs that are currently hidden/excluded. Currently, all UDFs are visible by default. UDFs can be moved from one list to the other. If a UDF is not visible, it is added to the database as an Excluded UDF for this Customer.

Select a UDF type Visible UDFs Available UDFs @ Orders Auto a Products Customer Ref

Order financial values Product financial values

When viewing a product or order, the UDFs are shown depending on the Customer UDF settings.

It is also possible to import UDF exclusions. The import file name for this is CUST_UDF_EXCLUSIONS.csv/txt

C.CODE - The customer name to which this exclusion applies. C.UDFTYPE - 2 character code indicating the type of the UDF. Values are PV, PF, OV, OF where P and O indicate Product and Order; F and V indicate Financial and Value. C.UDFNAME - The name of the UDF. C.UDFACTIVE - Whether the UDF is excluded or not. Values accepted are OFF to indicate the UDF is excluded and hidden for this customer or ON to indicate the UDF is visible.

Add User Notes to Products via the Multiple Update functionality

This enhancement allows the user to add a Note to multiple Products at the same time. This functionality is already available to Orders.

Select a previously saved profile How do you want to link these items Link value (wild cards allowed)

@ Orders 888 Product type Products ra) Cubic m/doz Enter note text

What value do you want to change

» Selling price

» Other direct cost » Ait Freight © Ignore critical path

© Design Brief Complete © Design Brief Skipped Save profile (© Sketch Complete

Product Notes can be displayed in Strip Hints

This functionality is already available for Orders and Strips.

Add a Product Note to the Product if the Capacity Factor changes

When FastReact Evolve is configured with variable capacity planning option, some clients use default Capacity Factor to enter number of resources required. This default resource requirement is updated

on Default capacity factor under Product - Add/amend - User Values tab. In order to enable this from FRS option need to enable Allow capacity factory to be defined by product.

- im 21/02/2022 Product “_test" has been created
- im 21/U2i2u2e Product type has been set to BLUUSE
- ay 21/02/2022 Timetable has been set to “Dev1—
- vm 21/02/2022 SEW LSMY) Work content: 20.000
- wm 21/02/2022 Twin Needle _SMY) Work content: 2.000

Consolidate Progress by Host Order

Ability to consolidate the order progress screen based on the Host order from the information already held in the database. The Host order field has been added to the Order field for consolidation on the consolidated order progress dialog.

a Report x Configure Close

Select order UDF for consolidation [_] De not include orders marked as complete Order : Auto Order : Customer Ref Product : Cubic m/doz Product : Sample Ref

Select order field for consolidation

Order base code Host order
