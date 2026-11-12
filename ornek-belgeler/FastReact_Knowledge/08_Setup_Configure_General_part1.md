# Main Menu - Setup - Configure - General (part 1)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > General
**Part:** 1 of 3 — sections: General Configuration, Defaults, Week numbers, General options, Incremental search lists, Late delivery calculation, Display, System audit trail notes

---

## General Configuration

*Context: Main Menu > Setup > Configure > General › General Configuration*

FastReact is an extremely flexible planning system that is used across many different industries. Each industry and even different business within the same industry will have specific requirements. As a result there are certain features within FastReact that are either not needed or simply not applicable to your specific implementation.

The Configure menu can be thought of as an 'on/off' switch for much of the functionality contained within FastReact along with certain technical settings that determine how the system will behave and how data will be stored.

This configuration will normally be set by the Fast React Systems representative during the installation process. Unless specifically instructed to do so, we strongly recommend that no changes are made to the Configure dialogs.

### Defaults

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults*

**Company name:** This shows the name of the Company which is held in the Licence Key This cannot be changed.

**Collaborative name:** If Collaboration is licensed, then this 5 character code is the ID for the Host system.

#### Week numbers

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › Week numbers*

**Enabled:** If enabled FastReact will display week numbers following the actual date in the format of [date] [week number]. The [date] will be formatted as per the Windows regional settings.

##### First week commencing date

The date of the first day of week 1 in the current year must be defined and also in the subsequent years before FastReact can calculate the current week number. These dates need only update once a year.

**Year 1:** The first week of year 1.

**Year 2:** The first week of year 2.

**Year 3:** The first week of year 3.

#### General options

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › General options*

**Hide sequence characters:** Many of the objects in FastReact need to be displayed in a particular sequence and this can be defined by prefixing the names of these items with a numeric code. This numeric code can be hidden in displays and reports by enabling this option.

> **Note:** For this to work your object names must contain at least one non numeric character.

**Allow wild cards (\* ?) in object names:** Because the filtering in the report generator makes great use if the wild card characters '\*' and '?' it may not be a good idea to allow these characters to be used in order and product codes as this could easily confuse the filtering. However, if these characters really must be used the user can disable this error checking here.

**Log to text file:** This is provided to help FastReact support staff to diagnose problems. Only turn this on if you are asked to by FastReact staff.

**Refresh data before all menu commands:** FastReact will check and incorporate any changes made by other users on a networked system. This may delay the opening of dialogs if there are many changes to be incorporated.

**Enable activity scheduler:** This option allows the user to schedule certain tasks on a timed basis in FastReact. These options are used in conjunction with the "Service" user. When enabled an Activity Scheduler menu option will appear on the main setup menu.

**Check table indexes on start up:** This option will allow FastReact to analyse the structure of the tables in the database upon start up.

**Cache operation schedules:** This option will allow FastReact to store operation schedules locally. This should only be enabled when ask by FRS support staff.

**Automatically compact Access database:** This provides for maintenance of Access databases. This should be enabled by default.

#### Incremental search lists

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › Incremental search lists*

**Products:** Enter the number of characters that must be typed before FastReact displays a short list of entries matching what has been typed so far.

If there are a very large number of entries starting with the same few characters (e.g. all your products may be prefixed with 'PO') then a short list of everything starting with PO is not very helpful. In this case set the value to 3 or more and a short list is only displayed after three characters are typed.

**Orders:** Enter the number of characters that must be typed before FastReact displays a short list of entries matching what has been typed so far.

If there are a very large number of entries starting with the same few characters (e.g. all your products may be prefixed with 'WO') then a short list of everything starting with WO is not very helpful. In this case set the value to 3 or more and a short list is only displayed after three characters are typed.

**Customers/Suppliers:** Enter the number of characters that must be typed before FastReact displays a short list of entries matching what has been typed so far.

**Materials:** Enter the number of characters that must be typed before FastReact displays a short list of entries matching what has been typed so far.

**Return entries:** The number of entries returned in the incremental search list can be specified . This will speed up the display of the list.

For example, a list of 5000 is much slower to display than a list of 50.

#### Late delivery calculation

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › Late delivery calculation*

This option allows the user to define which point in the process FastReact will use to calculate whether an order is on time or late, and by how much. FastReact will compare the difference between the specified delivery date and the selected point in the process. The options are:

**Arrive at customer:** This is the point at which the last product of an order arrives with the customer (default).

**Shipped from factory:** This is the point at which the last products are shipped from the final planned process.

**Complete in factory:** This is the point at which the last products are complete through all defined processes prior to final shipping. (The end of the strip plus any post planning board operations).

**End of last planned operation:** This is the point at which the last product is completed in the final planned process. (The end of the strip on the planning board).

#### Display

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › Display*

**Quantity decimals:** This allows the user to select the number of decimal places to be used when displaying order quantities, in particular production schedules where FastReact calculates daily rates to 3 decimal places.

> **Note:** All order quantities are always entered as integer values (no decimal place).

**Thousand separator:** These options will allow the user configuring the system to choose the type of separator:

**System:** FastReact will use the Windows system separator.

**Never:** FastReact will not use any separator.

**Always:** FastReact will always use a separator regardless in the Windows setting.

**System font name:** This field allows the font style to be changed within FastReact.

#### System audit trail notes

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › System audit trail notes*

**Enabled:** FastReact can maintain a chronological audit trail of all significant changes to Orders and Products. Each entry includes a date and the name of the user responsible for the change together with a descriptive comment.

> **Note:** This option will need to be enabled if you want to take full advantage of the change review feature.

**Include changes to UDF:** With this option enabled any changes made to any UDF field will be entered on to the audit trail notes.

**Enable notes archive:** This option will allow the user to save any notes for deleted Orders and Products in a network shared folder with each product or order in its own separate text file . Each file will include a date and the name of the user responsible for the deletion.

**Select folder for archive:** Specify where the archived notes will be saved to. This must be a shared folder on the network so that any user who deletes items will put the archived notes into the same location.

#### Document attach

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › Document attach*

Set up for the shared documents folder which will be the central repository for all external documents which can be attached to products, orders and/or customers.

#### Automatic Order Numbers

*Context: Main Menu > Setup > Configure > General › General Configuration › Defaults › Automatic Order Numbers*

When enabled, this option allows FastReact to automatically create Order and Purchase Order reference codes.

**Prefix:** The user can set a prefix which will be attached to the beginning of the auto generated Order or Purchase Order number.

**Length:** The user can set the number characters in the auto generated number here.

**Set next number ... (button):** This button allows the user to set the next auto generated number which will be applied to the Order or Purchase Order.

**Update (button):** This button will update any changes.

### Field sizes

*Context: Main Menu > Setup > Configure > General › General Configuration › Field sizes*

FastReact can support variable field sizes for text data. This means that the user can define text field lengths to be different from the standard pre-defined sizes. This offers considerable flexibility and allows FastReact to incorporate more easily with your current systems.

#### Select the field to change

*Context: Main Menu > Setup > Configure > General › General Configuration › Field sizes › Select the field to change*

Not all fields can be changed. However, the list can be extended, so if the required field is not in the list then please contact your supplier for a system upgrade (there may be a charge for this).

##### Fields currently available

- Customer description
- Customer name
- Customer user defined field
- Flow user defined field
- Material description
- Material reference
- Material user defined field
- Material variant
- Order description
- Order reference
- Order user defined field
- Plan group name
- Plan group user defined field
- Plan row user defined field
- Product description
- Product reference
- Product user defined field
- Product type user defined field
- Supplier name

**Default size:** This is the default size of the selected field.

**Maximum size:** This is the maximum size that the selected field can be expanded to.

**Current size:** This is the current size of the selected field.

**New size:** This is the new size which the user wishes the field to be.

There is a maximum of 250 characters for each field.

> **Note:** Screen displays may not be able to show the full field the size is excessive. The minimum size is 5 characters.

**Update (button):** This button will update any changes.

### Local machine

*Context: Main Menu > Setup > Configure > General › General Configuration › Local machine*

Settings on this tab only affect this workstation and the data is saved in the Registry on this machine

#### Folder in which local files will be saved.

*Context: Main Menu > Setup > Configure > General › General Configuration › Local machine › Folder in which local files will be saved.*

FastReact saves certain temporary files, log files and report pages on the local machine for each client to minimise network traffic. Specify the folder where you would like these files to be stored. By default this is 'C:\Fast_React'. FastReact will create a number of sub folders from this.

#### Folder in which translation file will be saved.

*Context: Main Menu > Setup > Configure > General › General Configuration › Local machine › Folder in which translation file will be saved.*

All text displayed in FastReact can be amended to your preference, e.g. you may refer to a 'Style' rather than a 'Product'. This also enables all of FastReact to be translated into other languages. The translation file is held by default in the folder 'C:\Fast_React' however you can select a shared network drive so that all users can access a common translation file. Users must have read access to this folder, and write access to update the translations.

#### Synchronise data frequency (minutes)

*Context: Main Menu > Setup > Configure > General › General Configuration › Local machine › Synchronise data frequency (minutes)*

Since FastReact is a multi-user system, new data or changes to existing data can come from several sources on the network. These changes are not instantly incorporated into the active planning board(s). However any workstation with an active planning board open will check with the central database for any changes every 'n' minutes. Entering '0' (zero) disables the function and changes will only be incorporated when the board is closed and reopened.

**Auto refresh (button):** This check box will cause FastReact to refresh without user intervention.

**Update (button):** This button will update any changes.
