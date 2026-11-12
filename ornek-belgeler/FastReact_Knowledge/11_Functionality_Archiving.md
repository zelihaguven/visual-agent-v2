# Functionality - Archiving

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Archiving

---

## Archiving.

*Context: Functionality > Archiving › Archiving.*

Introduction

As a basic premise FastReact loads orders and products into memory which means that as databases grow over time there can be an impact in performance doing basic everyday tasks. To improve this, FastReact has developed a new module, ‘*Archiving*’. Archiving enables the user to ‘*hide*’ unused products and orders thereby ensuring that day to day tasks are performed as quickly as possible. This document explains how to set up, manage and use archiving in a sensible effective way.

#### Orders

*Context: Functionality > Archiving › Archiving. › Orders*

Before the order can be archived it must meet certain conditions:

- The order must be completed and therefore no longer be loaded onto the planning board.
- The order should not be the parent of any other order.
- The order must not be part of a Purchase Order.

#### Products

*Context: Functionality > Archiving › Archiving. › Products*

The product however cannot be archived unless it meets certain criteria:

- The product must not be a parent product to any other product.
- The product must not be in use by any un-archived order.
- The product must not be linked into any design.

### Setting Up Archiving

*Context: Functionality > Archiving › Archiving. › Setting Up Archiving*

Archiving is an option that can only be controlled by the FRS user. To turn on or off Archiving, you must login in to FastReact under the FRS user and go to Setup - Configure - General - System. In this screen, under General options, there is a tick box for “*Archiving Enabled*”. To turn on Archiving ensure that this box is ticked:

[Screenshot: FRS Options]

### Using Archiving

*Context: Functionality > Archiving › Archiving. › Using Archiving*

Once Archiving is enabled as above it can be accessed by going to Tools - Archiving:

[Screenshot: Tools Archiving]

Under here there are 4 available options:

- Archive orders
- Un-archive orders
- Archive products
- Un-archive products

#### Archive orders

*Context: Functionality > Archiving › Archiving. › Using Archiving › Archive orders*

When you select “*Archive orders*” the following screen will appear. This window is used to search for specific orders based on any standard and UDF criteria within FastReact:

[Screenshot: Archive dialog]

#### Order reference

*Context: Functionality > Archiving › Archiving. › Using Archiving › Order reference*

Here, you can enter specific order references to find any orders that can be archived. You can either enter specific order numbers or use the drop down arrow to the right. The search field also enables searching with wild cards using ‘\*’.

#### Product reference

*Context: Functionality > Archiving › Archiving. › Using Archiving › Product reference*

You can search for any orders based around a shared product. You can either enter the specific product number, use a wildcard search for partial searches or use the drop down arrow to the right.

#### Created date between

*Context: Functionality > Archiving › Archiving. › Using Archiving › Created date between*

This search option enables you to search for any orders that were created between 2 specified dates. To select specific dates, click on the ‘down’ arrows to the right of each date field.

#### Customer

*Context: Functionality > Archiving › Archiving. › Using Archiving › Customer*

You can specify any customer for which orders are based by entering the customer name, selecting the customer name from the drop down window or using a wildcard search using ‘\*’.

#### User defined field

*Context: Functionality > Archiving › Archiving. › Using Archiving › User defined field*

Any orders can be searched by any customer specific User defined fields (‘UDF’s). Click on the down arrow to the right of the first window to select an existing UDF and in the second window you can enter text / numbers that are applicable to the selected UDF. You can also use ‘\*’ wildcard searches.

#### Latest delivery date

*Context: Functionality > Archiving › Archiving. › Using Archiving › Latest delivery date*

This search option enables you to search for any orders that have a latest delivery date set between 2 specified dates. To select specific dates, click on the ‘down’ arrows to the right of each date field.

#### Find

*Context: Functionality > Archiving › Archiving. › Using Archiving › Find*

Once any options have been set as above, click on this button to find all data that meets any or all defined criteria.

> **Note:** If NO data is entered, the find options will show ALL orders within the system that can be archived.

#### Clear all settings

*Context: Functionality > Archiving › Archiving. › Using Archiving › Clear all settings*

Clicking on this button will clear any specific data as defined in any of the above fields and will reset all date fields.

#### Results window

*Context: Functionality > Archiving › Archiving. › Using Archiving › Results window*

Any orders that meet ANY defined criteria will be displayed in this window, for example:

[Screenshot: Archived]

#### Selection criteria

*Context: Functionality > Archiving › Archiving. › Using Archiving › Selection criteria*

These buttons:

- Select all results.
- Invert the selected results, and
- Unselect all results.

#### Mark to be archived

*Context: Functionality > Archiving › Archiving. › Using Archiving › Mark to be archived*

Once search criteria have been set and results are displayed in the window, you will note the last column states “*To be archived*”. The default is set as ‘*Yes*’ and therefore “*Mark to be archived*” would only be used to revert any changes made to orders by clicking on “*not to be archived*”.

#### Not to be archived

*Context: Functionality > Archiving › Archiving. › Using Archiving › Not to be archived*

If the defined search fields result in orders being shown in the main window, there may be instances where some specific orders should not be archived. To ensure that this does not happen, you can highlight any order in the main window and click on ‘*Not to be archived*’. This will then change the ‘*Yes*’ to a ‘*No*’.

#### Archive selected

*Context: Functionality > Archiving › Archiving. › Using Archiving › Archive selected*

Once you have the orders shown in the main window, you can then archive by clicking on “*Archive Selected*”. Once selected you will note that the ‘*Yes*’ in the ‘*To be archived*’ column changes to ‘*Archived*’. If ‘*No*’ is selected that display changes to ‘no changes’. You will also note that in the bottom right corner, there is a count display:

[Screenshot: Archived]

### Un-archive orders

*Context: Functionality > Archiving › Archiving. › Un-archive orders*

This works in exactly the same principle as archiving orders but obviously performs the reverse of taking any archived orders and placing them back into the live environment.

All of the above searches can be utilised for unarchiving orders however there is one different option:

[Screenshot: Search]

‘*Show orders that cannot be unarchived*’ is a check box that will display orders that cannot be unarchived because the attached product is archived. If this is the case this fact will be displayed in the ‘To be unarchived’ column:

[Screenshot: Search]

In order for to be able to unarchive the requisite order, you must first unarchive the product.

### Products

*Context: Functionality > Archiving › Archiving. › Products*

The Archiving and Unarchiving of Products work in the same way as Orders.
