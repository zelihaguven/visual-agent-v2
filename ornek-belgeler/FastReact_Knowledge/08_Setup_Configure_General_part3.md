# Main Menu - Setup - Configure - General (part 3)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > General
**Part:** 3 of 3 — sections: Export data, Export file format, Options, Export file encoding (CSV and TXT), Reporting, Reporting options, Variance reporting, System

---

### Export data

*Context: Main Menu > Setup > Configure > General › General Configuration › Export data*

FastReact can export data to another system. Exporting is carried out using the report generator to provide extensive configuration and access to a rich data set. Data may be exported manually or unattended on a time schedule

#### Export file format

*Context: Main Menu > Setup > Configure > General › General Configuration › Export data › Export file format*

There are three options for export file formats:

- Comma separated (CSV)
- Tab separated (TXT)
- Database

Comma separated variable text file (\*.CSV), or Tab Separated variable text file (\*.TXT) produce files that can be opened in a word processor or in a spreadsheet. This format is ideal if the user wants to manipulate the data in a simple way.

Database format allows the user to write the exported data into an existing database so that it can be queried from another application. This method is ideal for creating tight links between FastReact and another application.

**Separator Character:** This option is only enabled if you are using the Comma separated variable text file (\*.CSV) export file type. By default CSV file have each cell in the report separated by a "," this may cause an issue depending on your regional setting on your PC. In this field the separator can be changed from being a "," to any other character such as ":" ";" etc.

**Override file extension:** FastReact will export data to the specified location and in the specified format, either .TXT or .CSV however the user may wish to change the file extension on the exported reports.

This option allows the user to do this so instead of exporting as a .CSV file it can be changed to a .XLS file.

**Export file location:** FastReact needs to know where to send the data files that you want to export. By default this is set to a folder called 'Export' that is located below the main folder specified for the local machine.

If Database format is selected then the user must enter the name of an existing database. Data can be exported to Microsoft SQL Server or to Microsoft Access. In the latter case the user must enter the full drive, path and database file name.

**Date format:** Many of the export files will include date fields e.g. Order delivery dates. This option enables you to determine the format of the date within the export file so that it is independent of the settings in Windows.

#### Options

*Context: Main Menu > Setup > Configure > General › General Configuration › Export data › Options*

This series of check boxes enable additional functions associated with exporting data.

**Enable scheduled exporting of data:** When enabled FastReact will automatically export data without any user prompts. The user can set either a time of day or a frequency for FastReact to run the export routine. To avoid several users automatically running the export routine inadvertently the automatic export will only run for a user called 'Service'. This user must be created under the security settings and must be logged into FastReact at the time specified on the auto-export set-up before the export will run unattended.

**Add timestamp to exported file name:** This option will place a Date and Time against the exported file. This allows the user to hold a history of exported files. Under normal circumstances, exported files will be overwritten.

**Export report as TAB separated file (default CSV):** When selected the export file will be formatted as TAB separated file. This setting is overridden when outputting Normalised data (see Report configuration) when the setting above (Export file format) will take precedence.

**Export CSV text with quotes (e.g. "ABC","XYZ"):** Text fields can be quoted. This prevents problems where the text data contains commas or other delimiting characters that might cause problems when reading into other systems.

**Export headers as first line of exported file:** When enabled the header of the report being exported will be included as the first line in the exported file.

**Export field names in file (default to users headers):** When enabled the FastReact internal field name will be included in the export file, rather than the user readable header. The latter is subject to translation whilst the former is not. In multi lingual installations it would be safer to use the internal field names as these will not be subject to change.

**Export only fields in report layout:** When enabled FastReact will only export the fields that are currently visible in the report, as defined in the report layout.

**Export data formatted as layout:** When enabled the data that is exported will be in the same sequence and format as defined in the report layout not as selected in the report designer.

**Scheduled export Time or Frequency minutes:** Enter either the time of day (using 24hr clock) or the frequency (in minutes) that you want to run the unattended export routine. The 'Enable scheduled exporting of data' option must also be checked.

**Do not export on the following days:** Select the days in the week that you do not wish the auto export of data to happen.

**E-mail error logs to:** Select the person (from the drop down list) who should receive any error logs for assessment after a scheduled export has taken place. Select 'none' to disable this option.

> **Note:** If the Activity Scheduler is enabled then the above options will be disabled.

#### Export file encoding (CSV and TXT)

*Context: Main Menu > Setup > Configure > General › General Configuration › Export data › Export file encoding (CSV and TXT)*

**Operating system default ANSI Encoding:** LATIN format character sets.

**UTF-8 Encoding:** Non - LATIN format character sets.

**UTF-16 little-endian byte order Encoding (Unicode default):** Non - LATIN format character sets.

**UTF-16 big-endian byte order Encoding:** Non - LATIN format character sets.

More information on ANSI and UTF encoding is available online.

### Reporting

*Context: Main Menu > Setup > Configure > General › General Configuration › Reporting*

This page contains various options relating to the way FastReact configures and calculates reports.

**Text displayed when zeros suppressed:** Enter a character which will appear on the reports when the zeros are suppressed on the report layout set up.

**Reporting days prior to today (0-365):** Enter the number of calendar days prior to 'today' that the date based reports are required show. A value of "0" will force all reports to start from today's date. A good choice would be 7 days as this would allow reporting of the current week. A value higher than this might be used if FastReact were not being updated regularly.

> **Note:** Certain reports are, by definition, historical in nature (e.g. production updates). This value is ignored for these types of reports.

**Reporting days beyond today (7-365):** Enter the number of calendar days forward from today that you want to report on. Do not enter a value that is larger than you really need as this will slow reporting a little.

**System default report font name:** The default font used in all reports is Arial, but this can be over-ridden on a report by report basis. If your system does not support Arial then you can select a different font here.

> **Note:** Only True Type fonts are available to ensure that printed reports appear the same as on screen.

**Send exported reports to folder:** This specifies the default destination of all exported files. This destination can be changed however, on a report by report basis

#### Reporting options

*Context: Main Menu > Setup > Configure > General › General Configuration › Reporting › Reporting options*

**Hide year on reports:** Enable this option to hide the year characters (i.e. 12/08/2002 will become 12/08) from any date-based reports. Using this option will reduce the required column widths on the report.

**Hide century on reports:** Enable this option to hide century characters (i.e. 12/08/2002 will become 12/08/02) from any date-based reports. Using this option will reduce the required column widths on the reports.

**Add week number to date:** This option will only be active if week numbers have been enabled (see Defaults above). When enabled, the week number will be shown next to the date on the planning board and any on any date-based reports.

**Show date and time for selected date fields:** This option will allow the reporting of the date and time in selected date fields.

**Insert thousands separator:** Enable this option if there is a need to insert the thousands separator (as defined in the Windows' Regional settings) into report numeric values.

**Support for emailing reports with Chinese characters:** This option will allow the emailing of reports which use Chinese characters.

**Do not allow negative W.I.P values:** FastReact can be configured to calculate the Work in Progress (WiP) of each order through the specified operations. In theory negative WiP values are impossible however negative WiP also highlights errors in data entry and/or recording. When enabled FastReact will display a zero on any WiP report instead of the negative value.

**Report N/A instead of a quantity for invalid operations:** This option will insert N/A into the reports where previously a quantity had been used for invalid operations.

**Include development events in order based reports:** When enabled you will be able to add both Development (Product) related events and Production (Order) related events to order based reports.

**Include skipped events in reports:** This option allows FastReact to report skipped events in all the reports.

**Refresh data before running reports:** FastReact holds its data in memory to give maximum performance. However this could mean that other users, in a multi-user system, could have made changes to the data.

e.g. production or event updates, and other workstations would not be aware of these changes until FastReact were closed and restarted (or a planning board opened).

This option forces FastReact to check to see if there are any changes that it is not aware of, and if so, to read those changes, thereby ensuring that reports are up to date.

**Include completed strips in strip reports:** This option allows FastReact to calculate dates for completed strips and so these can then be included in reports. Normally completed strips are ignored. Only dates from the start of production (i.e. not preparation) can be calculated in this way.

**Net delivered quantity from updated production flow:** This option allows FastReact to ignore any quantity that has been delivered to a client when calculating position against flow. FastReact will look at the current plan and compare it against a production flow, normally all historical updates are taken into account in this calculation and the reports reflect this, if however you turn this option on then if you enter a quantity in the order delivered field then this quantity will be taken off any flow reports.

**Include planned flow split by transport method in flow reports:** This option allows FastReact to filter the planned flow by transport method in flows reports.

**Include planned flow split by updated/planned in flow reports:** This option allows FastReact to filter the planned and unplanned flow in flows reports.

**Weeks to uplift row based schedules:** This is the number of weeks to uplift that will appear on the row based schedules reports.

**Background colour intensity:** This is where the background intensity is set.

#### Variance reporting

*Context: Main Menu > Setup > Configure > General › General Configuration › Reporting › Variance reporting*

**Number of forward days to retain:** This is the number to days in the future that FastReact will retain for variance reporting.

**Update (button):** This button will update any changes.

### System

*Context: Main Menu > Setup > Configure > General › General Configuration › System*

> **\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*:**

> **Note:** This section is only available with the FRS logon and requires the FastReact Account Managers approval when enabling any options.

> **\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*:**

#### Order options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Order options*

**Show Contract Qty field:** Enabling this option will display the Contract Qty field on the Orders dialog.

**Allow Bill of Materials items to be disabled:** This option will allow users to set materials on a BoM as disabled without having them removed from the BoM.

**Retain order schedules comparison reporting:** Enabling this option will display the Retain order schedule button on the Order dialog and allow the saving of the current Order schedule.

**Extended order status:** Enabling this option will display the User Status field on the Order dialog and allow the user to configure the Extended Order Status on the Setup dialog.

**Enable host order substitution (single delivery only):** This option will display the Host order substitution field on the Planning tab of the Orders dialog. It will also allow the user to use the Substitution functionality within FastReact.

**Allow host order over-substitution:** If Host Order Substitution is enabled, this option will allow over substitution of the Host Order.

**Allow finalisation of host order:** If Host Order Substitution is enabled, this option will allow users to "close" or complete Host Orders.

**Allow batch creation using ticket batch quantity:** If Batch Tickets are enabled then this option will the batch creation via the Ticketing functionality.

**=>Mark as complete batched host orders:** Used in conjunction with the above option, this allows the completion of batched host orders.

**Make batch numbers specific to orders:** With this option enabled, each Order will have its own specific batch number.

**Copy standing time on substitution:** If Host Order Substitution is enabled, this option will copy the Host Orders standing time to the substituting order when it is substituted.

**Copy timetable on substitution:** If Host Order Substitution is enabled, this option will copy the Host Orders timetable to the substituting order when it is substituted.

**Copy event progress on allocation of host:** If Host Order Substitution is enabled, this option will copy the event progress to the substituting order at the point when the Host order is linked to the substituting order. This will occur when an Order name is entered in the Host Order Substitution field on the substituting Order dialog.

**Copy event progress on substitution:** If Host Order Substitution is enabled, this option will copy the event progress from the Host Order to the substituting order when it is substituted.

**Copy event base date on substitution:** If Host Order Substitution is enabled, this option will copy the event base date from the Host Order to the substituting order when it is substituted.

**Copy transport method on substitution:** If Host Order Substitution is enabled, this option will copy the transport method from the Host Order to the substituting order when it is substituted.

**Allow production updates to be transferred to another order:** This option will enable the Transfer dialog under the Orders menu and allow production to be transferred from one Order to another Order.

**=> Skip quantity reduction checks during imports:** This option should be used in conjunction with the above option and it will prevent Order reduction checks being performed on transferred Orders.

**Hide allocate to plan:** This option will hide the Allocate to Plan Orders menu option. There is no need for Allocate to Plan if a system has a High Level Planning Board.

**Update description when product changes:** If there is no Order description defined on an Order then the Product description is automatically copied to the Order description. This option will allow this "Order description" to be updated when the Product is changed.

**Unreserved supply is exclusive to unreserved demand:** This option will exclude any unreserved supply from the demand.

**Reserve order status:** This option will enable the Reserve options on the Orders dialog.

**Property matching on orders:** This option will enable the Override property match on the property tab of the Orders dialog.

**Enable hyperlinks:** This option allows web links to be stored against an Order. The link behaves like a hyperlink and opens the location, in a browser, when it is clicked on.

#### General options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › General options*

**Require conformation of routing before planning:** This option only applies to the Parallel Routing licence option and will force the user to check that the Product has a valid routing before the Order can be planned.

**Archiving Enabled:** This option will enable Archiving in the FastReact system. The Archiving dialogs will appear under the Tools menu and an Archive check box will appear on the Orders and Products dialogs.

**Enable Grid data entry:** This option should be used instead of Tabular Entry. This will allow the use of the Grid data Entry dialogs under the Orders and Products menus.

**Process Excel order imports:** This option is a client specific option to allow the import of Excel files. This is very specialised and should not be used without contacting Fast React UK.

**Log update differences:** This is another client specific option to log update differences. This is very specialised and should not be used without contacting Fast React UK.

**Enable import file errors to create export files:** With this option enabled, an export file is created from ant import errors.

#### Product options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Product options*

**Enable operation descriptors:** This option will turn on the Operation Descriptors and allow the user to define then in FastReact.

**Enable WiP overlap quantity:** When enabled this option will allow the WiP Overlap quantity to be defined on Products dialog under the User values tab. It is only applicable to systems with multiple planned operations/stages.

**Allow Bill of Materials items to be disabled:** This option will display the "Disable" column on the Materials tab of the Product or Order allowing that material to be disabled on the product but still attached to the BoM.

**Allow capacity factor to be defined by product:** When enabled this option will display the Capacity Factor field on the Product dialog under the User values tab.

**Enable minimum quantity per operation:** When this is enabled two columns, Min Qty and Inc Qty, will appear on the Product work content matrix on the Product dialog.

> **Note:** This is a client specific option.

**Allow MRP uplift by product:** This option will display the MRP uplift percent (imported) field on the Materials tab of the Products dialog.

> **Note:** This is a client specific option.

**Enable hyperlinks:** This option allows web links to be stored against a Product. The link behaves like a hyperlink and opens the location, in a browser, when it is clicked on.

#### Customer options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Customer options*

**Show Customer group:** This option will allow the user to see the Customer Group tab on the Customers dialog and allow them to define these Groups.

**=> Hide items where customer not in a valid group:** This option should be used in conjunction with the above option and will hide orders etc when the customer is not in a valid or defined group.

#### Planning options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Planning options*

**Allow low level consolidated strips:** This option will allow the user to consolidate strips on the Low Level board. The consolidation button will be visible on the Low Level boards when this is enabled.

**Plug out by Group:** When this option is enabled the user will be able configure and send Plug Out boards by Planning Group.

**Spread operation schedules over full week:** This option will spread the operation schedules over the full working week.

**Allow despatch plan schedules in the past:** This option allows despatch schedules to be in the past instead of replanning them automatically to "todays" date.

> **Note:** This is a client specific option.

**Split Made Strips by capacity factor:** When this option is enabled, FastReact will create strips split between different capacity factors. When not checked the capacity factor will still be stored in the _PLAN_UPDATES table but made strips will always use zero and not create different strips for different factors within the same row/group/etc.

**Auto JiT Plan all orders:** This option automatically JiT plan all orders and is designed for clients who only use the Pre-production board and never plan any strips at High Level or Low Level.

> **Note:** This is a client specific option.

**Do not JiT if order has retained event dates:** This option will prevent the Orders from automatically planning or replanning if there are any retained dates against it.

**Enable plan Autosave option:** This option will save the planning board in the event of a crash and allow the user to return to the plan at the point in time of the crash. This should not be enabled for any clients without first consulting UK Support.

> **Note:** This is a client specific option.

**Allow low level groups to be hidden:** This option will make the Hide Group button available on the Low Level board which will allow the user to filter out the Groups that they don't want to see.

**Same fields for Low Level accept/load lists:** This option will force the Low Level Accept list field headers to match the configured Low Level Load List field headers.

**Use time specific WiP calculations:** > **Note:** This is a client specific option.

**Cascade WIP through operations:** > **Note:** This is a client specific option.

**Cascade Supply/Demand through operations:** > **Note:** This is a client specific option.

**Hide "Deallocate Order" tab on Low Level Load list:** This option to Deallocate a Strip/Order from the Low Level Load List will be hidden when this option is enabled.

**Split strips in specified multiples:** This option will automatically split a strip is to the specified number when enabled. This will be defined on the Operations setup against the planned operation.

**Property linking on rows:** This option will display the Row Link Property field on the Plan Row dialog.

**Hide material issues if "No Material Required":** This option will hide all the material issues

**Allow default initial strip length to be specified by stage:** This option allows the system to have initial strip lengths defined by stage in a multi stage system.

#### Pre Production planning board options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Pre Production planning board options*

**Show "Split order" option:** This option will allow the user to Split an Order on the Critical Path planning board. An option will appear when the user right clicks a Order on the Pre Production board. This option, "Split Order", will display the Split Order dialog and allow the user to define and split an Order.

#### Material options

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Material options*

**Allow setting of MRP calc. results period from menu:** This option will allow the user to define the MRP period that the MRP calculation takes. This is done from the Materials menu option.

#### Excel Locale Override

*Context: Main Menu > Setup > Configure > General › General Configuration › System › Excel Locale Override*

**Short Date Format:** This option allows the date format of the Excel sheet to be set, overriding all local PC settings.

**List Seperator:** This option allows the separator of the Excel sheet to be set, overriding all local PC settings.

**Update (button):** This button will update any changes.
