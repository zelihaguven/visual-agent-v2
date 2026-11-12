# Main Menu - Reports - Reports (part 1)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports
**Part:** 1 of 3 — sections: Reports, Select, Designer, General, Warning, Advanced, Import/Export

---

## Reports

*Context: Main Menu > Reports › Reports*

Multiple reports can be opened and moved about the computer screen using the FastReact reporting module. This FastReact module also has the ability to have the Reports open and running at the same time the Planning Boards are open.

To use FastReact to it’s fullest potential the user will need to produce many different kinds of reports that will give meaningful and accurate information to internal and external departments within your business. To satisfy the various needs of different companies FastReact is equipped with a reporting tool which allows the users to build reports to suit their specific requirements.

All of the reporting functions can be found under the Reports main menu option. These functions include the Report Designer which allows the user to identify the content of a report; the Report Layout editor which allows the user to specify how the selected data is displayed on screen and on the printed page; and the Report Configure dialog which allows the user to sort and filter the report to contain just the specific data required.

Each of these sections is covered below together with a full list of all Report Data Fields that are available. When created reports become available in the Report Selection dialog, also described below. This also gives access to the other functionality (above) as appropriate.

The dialog has the following main tabs.

- Report designer = First stage in building a new report.
- Import/export tab = Import and export report definitions and layouts into and out of FastReact.
- Report layout tab = Define how the report will look on screen and on paper.
- Report selection = Choose which report to run.
- Report configuration = Filter/sort and further report configuration.
- Preview/Print = Show the report on screen or send to printer/file/e-mail.

**Configuration Mode:** Unchecking this option will force FastReact to skip the Configuration dialog on the selected report. Instead, FastReact will preview the report. Leaving this option checked will allow the user to access the configuration dialog.

### Select

*Context: Main Menu > Reports › Reports › Select*

All of the reports that have been created are available though this dialog. However, some reports may not be available to certain user groups according to the access rights that have been assigned to each group.

##### Report group

This is a list of report groups that you have created in the Report Designer. Select a group to list all of the reports that are within that group.

##### Report layout

Each report will have only one data definition, but can have any number of different ways to display that data. By default FastReact creates a configuration called '<Standard>' for you to use, but you can create others as described in the Report Configuration section. Where there are more than a single variant you may select it here.

> **Note:** You can delete unwanted report variants by right clicking on its name and confirming deletion when prompted. You can delete the <Standard> report and FastReact will create a new one for you the next time the report is selected.

**Description:** Report layout variations are given a short name and a description. By default FastReact shows the short name in the list but you can display the description instead by checking this box.

##### Selection

Certain reports allow additional selection to be made.

For example the user may want to report a production schedule for a specific operation. In this case the selection will list all operations and the user can then select the required one. In this way the same report definition and layout can be used more flexibly.

##### Bespoke Reports

FastReact has the ability to display specific customised reports for the user. These FRS designed reports are highly client specific and require Report Development from the FastReact Development team. Once created and imported into FastReact, these Bespoke reports will appear in this drop down list. This is a Licenced option and does not allow clients to create their own Bespoke Reports.

### Designer

*Context: Main Menu > Reports › Reports › Designer*

The purpose of the report designer it to allow the user to create new reports and edit existing ones. This part of the report generator only concerns itself with the content of the report and not its visual layout. See Report Layout Editor for details.

Each report must be given an internal name, to be used by FastReact and a name that will be recognised when selecting reports to run. Also, reports may be functionally grouped to keep, for example, Production reports separate from critical path event reports. The grouping is the users choice and can be changed at a later stage as necessary, as can the user name for the report. Only the internal name is fixed once the report is created.

#### General

*Context: Main Menu > Reports › Reports › Designer › General*

##### Identification

**Identification:** This offers a list of previously created reports for editing or deletion.

**Definition file:** This is the internal name and can accept up to 20 alpha numeric characters; spaces are not allowed.

**Report Group:** This field accepts up to 20 alphanumeric characters. Type into this field the name of your report group, or select an existing group from the drop down list. Reports in different groups will be visually segregated in the Report Selection dialog.

**Description:** The entry which is make here will be the main means of identifying this report in the future so make the entry descriptive so that it will not get confused with another report. The user can enter up to 50 characters for this description.

> **Note:** Other users may well be running these reports so a good description is desirable.

**Save (button):** Click here to save your report definition to the database. Once saved all other (valid) users will be able to access it.

**Save As (button):** You can use this function to make a copy of an exiting report. Select the report and click Save As. You must then enter a new name and click the Save button.

**Delete (button):** Use this to permanently remove a report from FastReact.

##### Data List

**Select main loop:** The user must select a main loop for each report. The choice of loop is a logical one as a report which must list all orders would need the Order Loop, whilst one which listed Products would need the Product loop. A little care in selection is required as in the example below.

For example, if the user wants to report a list of all the Products the most appropriate loop would be 'Product'. It would be possible to use the 'Order' loop to provide a list of Products since all Order records must contain a Product and so Product data is available for each order. However, since there may be several orders for the same Product, a 'Product list report' using 'Order' as the loop may list the same Product several times. By the same token some Products may be missing from the list altogether (there may be no active Orders for a valid Product).

Whichever loop is selected, FastReact will make sure that the data fields that the user includes are valid for that loop. A detailed description of Main loop selection may be found in the Report Data Fields section below

##### Field Groups

The data available for reporting is presented for selection as a number of Field Groups. These link logically connected field data, so there is, for example a field group for Orders, another for Product and another for Customers and so on. Each of the field groups is described fully in Report Data Fields Not all field groups are available at any one time as this depends on the selection of the report main loop, described below.

##### Available data fields

This list will contain all data fields that are available for the selected field group.

> **Note:** Any data fields that have already been selected into a report will have been removed from this list so that the same data field cannot be selected more than once.

The user selects data fields into a report by double clicking Them. They will then be transferred to the Selected fields list. Selected fields can be de-selected in the same way.

Fields that are not valid for a particular Loop will be grayed out. Selecting one of these will result in an error message.

**Field name toggle (button):** - [Icon: Show Names] Show import field names.

##### Selected data fields

Data fields included in the report are shown in this list. De-select by double clicking on the field to be removed.

The sequence that the data fields appear in the list is important if the report will be exported in Normalized format. As a rule, when creating new reports it is better to have any fields which might be used for filtering the report content at the top of the list as this is the sequence in which they will be displayed in the Filter Grid. Use the Up and Down buttons to change the sequence as appropriate.

In some cases the data field may refer to a group of values, for example to get data for the Operation schedule you would need to select the operation to report. In this case the Selection field will show what is to be selected, in the above example 'Select an operation'. The user will make this selection when the report is run and not here.

> **Notes on data field selection:** Data fields can be selected from different Field groups based on logical rules. For example each order MUST have a product so all product data is available when running a report which uses the Order main loop. Likewise Customer information may also be included as there is a logical link between an Order and a Customer or Product. However, if you select the Product loop then Order data is not logically available as there could be several orders for one product and the report generator would not be able to choose which order to put with that product. A full definition of field selection may be found in Report Data Fields.

## Warning

*Context: Main Menu > Reports › Warning*

If the user plans to export the report in normalized format then the repeating fields MUST be configured on the Report Designer so that they are at the end of the list. Repeating field which are marked as non-repeating MUST also be towards the end of the list.

For example:

1. Normal non repeating fields
2. Repeating fields (marked as non-repeating)
3. Repeating fields.

**Move report (button):** - [Icon: Up Down] Use the up and down arrows to move report fields.

**Field check (button):** - [Icon: tick] Check for fields used in the report.

This button will analyse the selected report and highlight the field which are not included in any variant of that report. This allows the user a quick check for redundant data which FastReact has to find in order to build and run the selected report. Any highlighted field can then be removed from the data fields List.

##### Security

The list will contain all user groups that have been defined. Select those groups that will need to run the report. The report will not be available to users in other groups. FastReact will warn the user if a report is created with no user groups selected, however you can still save the report as the Supervisor user will have access.

#### Advanced

*Context: Main Menu > Reports › Warning › Advanced*

##### Reporting days prior to today (0-365)

**Override default:** Checking this box will override the default global days as set on the Report tab on the Setup - General dialog. The user can then enter the number of calendar days prior to 'today' that the selected date based report are required show. Unchecking the check box will force the report to use the global settings.

> **Note:** The global setting for all reports can be seen in brackets beside the check box.

##### Reporting days beyond today (7-730)

**Override default:** Checking this box will override the default global days as set on the Report tab on the Setup - General dialog. The user can then enter the number of calendar days forward from today that the selected date based report are required show. Unchecking the check box will force the report to use the global settings.

> **Note:** The global setting for all reports can be seen in brackets beside the check box.

##### Reporting options

This option box will show the global setting for the listed option and will allow the user to change these for the selected report.

> **Note:** The default setting will be the global setting.

###### Key explanation

| [Screenshot: selection] | - Override default. Use in this report regardless of the global setting. |
|---|---|
| - Override default. Do not use in this report regardless of the global setting. | |
| - Use default. This report will use the default global setting. | |

**Hide year on reports:** Enable this option to hide the year characters (i.e. 12/08/2002 will become 12/08) from any date-based reports. Using this option will reduce the required column widths on the report.

**Hide century on reports:** Enable this option to hide century characters (i.e. 12/08/2002 will become 12/08/02) from any date-based reports. Using this option will reduce the required column widths on the reports.

**Show date and time for selected date fields:** This option will allow the reporting of the date and time in selected date fields.

**Insert thousands separator:** Enable this option if there is a need to insert the thousands separator (as defined in the Windows' Regional settings) into report numeric values.

**Include development events in order based reports:** When enabled you will be able to add both Development (Product) related events and Production (Order) related events to order based reports.

**Include skipped events in reports:** This option allows FastReact to report skipped events in all the reports.

**Include completed strips in strip reports:** This option allows FastReact to calculate dates for completed strips and so these can then be included in reports. Normally completed strips are ignored. Only dates from the start of production (i.e. not preparation) can be calculated in this way.

**Net delivered quantity from updated production flow:** This option allows FastReact to ignore any quantity that has been delivered to a client when calculating position against flow. FastReact will look at the current plan and compare it against a production flow, normally all historical updates are taken into account in this calculation and the reports reflect this, if however you turn this option on then if you enter a quantity in the order delivered field then this quantity will be taken off any flow reports.

**Include planned flow split by transport method in flow reports:** This option allows FastReact to filter the planned flow by transport method in flows reports.

**Include planned flow split by updated/planned in flow reports:** This option allows FastReact to filter the planned and unplanned flow in flows reports.

### Import/Export

*Context: Main Menu > Reports › Warning › Import/Export*

In addition to creating reports manually as described above the user can also Import and Export reports from media such as CDs or disk drives. This functionality was provided so that 'standard' reports, supplied with FastReact could be imported from the installation package.

Import report definition

**Browse (button):** - [Icon: Browse] Browse for the required report.

On the left hand side of this tab there is a browse button so that the user can select the location to Import reports from.

Click here and locate the folder in which the report files are to be found. Any reports found in this location will be shown in the list box at the top of the dialog. Report files have the extensions of '.RDF' and '.RCF', the former holding the definition of data fields and the latter holding report layout information. Each report comes with one layout by default but there could be many variants of the same report.

##### Available reports to import

This is a list of all the reports available for import from the source location.

**Import all reports:** This option will import all the reports from the source location.

**Import all layout variations:** This option will import all the layout variations from the source location.

**Overwrite existing reports:** This option will overwrite any existing reports in FastReact with the imported reports from the source location.

**Import as:** This option allows the user to import individual reports and save them under a different name.

**Import (button):** This button will start the importing of the selected reports.

##### Export report definition

**Reports to export:** This is a list of all the reports in the current FastReact system.

**Export all reports:** This option will export all the reports from FastReact.

**Export all report variants:** This option will export all the layout variations from FastReact.

**Export report to:** Using the browse button the user must select the location to which the selected reports will be exported to.

**Browse (button):** - [Icon: Browse] Browse for the required export destination.

**Export (button):** This button will initiate the exporting of the selected reports.
