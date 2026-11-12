# Main Menu - Setup - Configure - General (part 2)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > General
**Part:** 2 of 3 — sections: Importing data, Import file format, Date format, Scheduled import time, Options, Do not change values when importing data

---

### Importing data

*Context: Main Menu > Setup > Configure > General › General Configuration › Importing data*

**Import file location:** FastReact needs to know where to look for the data files that you want to import. By default this is set to a folder called 'Import' that is located below the main folder specified for the local machine (see Local machine) although this can be any directory on your network that is visible from this workstation.

#### Import file format

*Context: Main Menu > Setup > Configure > General › General Configuration › Importing data › Import file format*

There are three options for import file formats. Either Comma separated variable text file (\*.CSV), or Tab Separated variable text file (\*.TXT) or SQL table format. Select the format that you prefer.

#### Date format

*Context: Main Menu > Setup > Configure > General › General Configuration › Importing data › Date format*

FastReact supports a number of different date formats. The format required must be set here to be independent of the settings in Windows. The import files will still work, even if the date format is changed on the machine doing the import.

#### Scheduled import time

*Context: Main Menu > Setup > Configure > General › General Configuration › Importing data › Scheduled import time*

FastReact can import data automatically according to rules you define here.

> **Note:** For this to work automatic importing needs to be enabled in the Import options described below. Additionally only a single computer on the network must be able to perform the import at any one time. To ensure this only a user logged on as 'Service' may import data automatically.

**Scheduled import time:** Set the time of day, in 24 hour format, that you want the import to start.

OR

**Scheduled import frequency:** FastReact can trigger an import to happen on a set frequency. If you set both time of day and frequency the time of day will be ignored.

**Do NOT import on the following days:** You may not want to trigger the import every day. You set the days to miss here

> **Note:** If the Activity Scheduler is enabled then the above options will be disabled.

**Email error logs to:** A specific person may want to be notified if an import fails for any reason. Clearly the importing machine must have a valid email connection for this to work. Select the recipient from a list of users with valid email addresses. This can be tailored to function in the Import options.

#### Options

*Context: Main Menu > Setup > Configure > General › General Configuration › Importing data › Options*

This list allows the user to further refine the import functionality to suit specific circumstances and problems

**Delete all FastReact orders missing from the import file (select only one):** When enabled any Orders that do not appear in the Orders import file will be automatically deleted from FastReact. This can be useful to maintain the FastReact database and the host database in synchronization. Use this option with caution, as deleted Orders cannot be recovered.

**Report all FastReact orders missing from the import file (select only one):** When enabled any Orders that do not appear in the Orders import file will be reported in FastReact. A note will appear in the orders dialog informing you that the order was missing from the import file. This can be useful to check data integrity between FastReact and the host system.

**Complete all FastReact orders missing from the import file (select only one):** When enabled any Orders that do not appear in the Orders import file will be automatically completed in FastReact. This can be useful to maintain the FastReact database and the host database in synchronization.

**Advanced management of orders missing from the import file (select only one):** When selected this provided the option to Ignore, Report, Complete or Delete order that are missing from the orders import file. These option are order status specific.

**Delete all FastReact orders that are status "9" or status "X":** Orders that exist within FastReact and have one of the above status when imported will be deleted on import. If this option is not selected the orders will be retained in FastReact but will be marked as complete.

**Allow import of Order with duplicate delivery dates:** This option will allow the importing an order which has more than one delivery on the same day.

**Import cumulative production updates by Order:** There are two methods for recording production updates:

- Incremental (default), where the quantity made on the specified date is added to previous total. If the same file is accidentally imported twice then this method can double book entries and;
- Cumulative, where the total quantity made to date is imported every time. This method allows the same file to be imported several times without double booking as the total quantity is always taken.

Only planned operations can be set to receive incremental updates, all non-planned operations are imported as cumulative figures for each Order. For the planned Operations there are several cumulative methods which may apply as below.

**Import cumulative production updates by Group:** When enabled, production figures in the import file should contain the cumulative production progress for each Order within each planned Group,

i.e. if an Order is split across two planning Groups then the cumulative figure for each Group must be entered (along with a Group reference). The total Order progress will be the sum of each Groups' cumulative progress.

**Import cumulative production updates by Row:** When enabled, production figures in the import file should contain the cumulative production progress for each Order on each Planned Row.

i.e. if an Order is split across two or more planning Rows then the cumulative figure for each row must be entered (along with a Row reference).

The total Order progress will be the sum of each Rows' cumulative progress.

**Ignore operations with zero progress values:** When enabled, any non planned operation production updates of zero quantity in the import file will be ignored.

**Skip cumulative updates with zero quantity:** Where cumulative planned operation production updates are imported a zero quantity value will, essentially, clear any previous updates. This can be problematic if planned updates are both manually entered, whilst non planned operations are imported. Setting this option will prevent loss of the manual planning board updates.

**Import normalised production updates:** If the import file contains normalised data then this option will allow the importing of that data. This option must be enabled when importing the UPDNORM or UPDATE, (by Size), import files.

**Use Product Type values as Product defaults:** When enabled FastReact will infer the properties (work content etc.) of a Product Type into a new Product during the initial import. For further details see Importing Products.

> **Note:** If the Product already exists then the Product Type values will NOT over-write the existing values.

**Calculate product work content x product type work content:** This option will multiply the imported product work content with the work content defined on the product type for that product.

**Use Product Mask values as Product defaults:** When enabled FastReact will infer the properties (work content, product type etc.) of an existing product into a new Product during the initial import. The Product from which the properties are inferred is known as the 'mask'. In order to link a new Product (child) to the mask, a number of characters are specified.(see below) If the values associated with the mask Product are changed the relevant values in the child products are NOT altered. To do this you need to inherit properties as below.

**Inherit work content from Product mask (defaults to copy):** When enabled the work content is inherited from mask to child rather than copied, thus any changes in the mask are automatically flushed though to all children of that mask.

**Inherit property from Product mask (defaults to copy):** When enabled the Product property string is inherited from mask to child rather than copied.

**Inherit materials from Product mask (defaults to copy):** When enabled the materials are inherited from mask to child rather than copied.

**Clear all material stock and deliveries before importing:** When enabled all existing material stock and expected deliveries records within FastReact will be deleted (see also below).

**Zero material stock (leave material data intact) before importing:** This is used in conjunction with 'Clear all material stock and deliveries before importing' (above) When enabled all material stock values will be set to zero. If not enabled the material record itself will be deleted.

**Ignore material expected schedules for materials that exist as FastReact products:** This is only valid when using vertical planning. When selected FastReact will ignore any material schedules for materials that are planned in FastReact. This is because the material schedule will be determined from the planning board.

**Clear ALL Order BoMs before importing OMATS:** This option will remove all Order bill of materials, regardless of Order Status, prior to importing the Order Material TXT or CSV import file.

**Clear CONFIRMED order BoMs before importing OMATS:** This option will remove all Confirmed Order bill of materials prior to importing the Order Material TXT or CSV import file.

**Clear PROVISIONAL order BoMs before importing OMATS:** This option will remove all Provisional Order bill of materials prior to importing the Order Material TXT or CSV import file.

**Clear SPECULATIVE order BoMs before importing OMATS:** This option will remove all Speculative Order bill of materials prior to importing the Order Material TXT or CSV import file.

**Clear TRANSIT order BoMs before importing OMATS:** This option will remove all Transit Order bill of materials prior to importing the Order Material TXT or CSV import file.

**Clear ALL Product BoMs before importing PMATS:** This option will remove all Product bill of materials prior to importing the Product Material TXT or CSV import file.

**Prevent importing of products with unknown sizes:** This option will prevent the importing of a product if the size on the product does not already exist in Evolve.

**Ignore material expected schedules for materials that exist as FastReact products:** This option will not import material expected schedules for materials that are marked as a Product.

**Purge specified orders before importing:** When enabled FastReact will purge (delete) orders specified before importing. The orders to be deleted are defined in the Control string detailed below

**Add field headers from separate header file:** When enabled FastReact will look for a header file to establish the layout of the data provided. This is used for importing data from other systems into FastReact where those systems are not able to insert a header column in the file. The header file will have the same name as the import file with a file extension of .HDR

**Use compliant import file field names:** Occasionally systems cannot use the standard FastReact field header name formats, with special characters, for example, ".", "^", "~" and ":". Since these characters are used within FastReact as field names, problems can occur when importing data from other systems. When enabled this option will allow these special characters to be replaced with valid numeric characters that dBase files can recognise. The conversions are shown in the following table:

| FastReact | Conversion |
|---|---|
| . | 1 |
| ^ | 2 |
| ~ | 3 |
| : | _ |

**Allow import of data from multiple files:** This option enables FastReact to import multiple import files.

For example, it there are Order files called, Orders, Orders1, OrdersA, then with this option enabled all of these Orders files will be imported.

**Strip surplus quote delimiters from imported data:** When enabled FastReact will remove any extra " " from the import file fields.

**Skip change log mechanism for faster imports:** The user may find that due to the size of your import files that they take a while to import, if this option is enabled then FastReact will skip various internal checks which will speed up the importing of data into the system. Without having a detrimental effect on the database.

**Enable scheduled importing of data:** This option allows for unattended data import into FastReact. The user will also need to set up the time of day and days of the week or, alternatively, the frequency of importing. (See above).

**Do not E-Mail successful imports:** By default FastReact will email to the nominated recipient (See above) notification of import completion. Enable this option if you only want to send notification of failures.

**Log successful imports to text file:** This option will create a log file which will contain all of those items you have successfully imported. The file is called 'IMPORTED.TXT' and is held in the 'LogFiles' folder below the main folder specified for the local machine. See Importing data.

**Retain import files (timestamp) after all imports:** This option will place a Date and Time against the imported file. This allows the user to hold a history of imported files. Under normal circumstances, imported files will be overwritten.

**Use export encoding when importing:** This option allows the importing to be defined as a certain encoded type. This is particularly useful for non LATIN character sets.

**Convert ANSI files to UTF-8:** This option will convert a ANSI import file to a UTF-8 encoded file. This is useful if the system producing the import file can only produce ANSI encoded files but the FastReact system is setup for non LATIN character sets.

**HOTFIX: Reset buffer for each line read. Only use if odd characters are mis-translated:** This option should only be enabled if some of the non LATIN character sets are not being imported correctly.

**Use automatic importing when files are changed:** This option automatically import files if FastReact detects a change in them.

**Allow import file location to be overridden locally:** This option allows the local user to override the Network import location.

#### Do not change values when importing data

*Context: Main Menu > Setup > Configure > General › General Configuration › Importing data › Do not change values when importing data*

Further importing options are available when this button has bean clicked. A sliding dialog will appear with the following options:

**Do not change product Product type:** With this option checked, the Product Type on the Product will not be altered if the Product is re-imported with a different Product Type on the Product import file.

**Do not change product Work content:** With this option checked, the Work content on the Product will not be altered if the Product is re-imported with a different Work content on the Product import file.

**Do not import new orders:** With this option checked, new Orders on the Order import file will not be imported.

**Do not change order Product:** With this option checked, the Product on the Order will not be altered if the Order is re-imported with a different Product on the Order import file.

**Do not change order Customer:** With this option checked, the Customer on the Order will not be altered if the Order is re-imported with a different Customer on the Order import file.

**Do not change order Status:** With this option checked, the Status on the Order will not be altered if the Order is re-imported with a different Status on the Order import file.

**Do not change order Timetable:** With this option checked, the Timetable on the Order will not be altered if the Order is re-imported with a different Timetable on the Order import file.

**Do not change order Event base date:** With this option checked, the Event base date on the Order will not be altered if the Order is re-imported with a different Event base date on the Order import file.

**Do not change order move days:** With this option checked, the move days on the Order will not be altered if the Order is re-imported with a different move days on the Order import file.

**Do not change order Deliveries:** With this option checked, the Deliveries on the Order will not be altered if the Order is re-imported with a different Deliveries on the Order import file.

**Do not change order Plan in Group:** With this option checked, the Plan in Group on the Order will not be altered if the Order is re-imported with a different Plan in Group on the Order import file.

**Do not change order Contract quantity:** With this option checked, the Contract quantity on the Order will not be altered if the Order is re-imported with a different Contract quantity on the Order import file.

**Do not change existing "Confirmed" orders:** With this option checked, existing Confirmed orders within FastReact will not be changed regardless of what the Order import file says.

**Do not change existing "Provisional" orders:** With this option checked, existing Provisional orders within FastReact will not be changed regardless of what the Order import file says.

**Do not change existing "Speculative" orders:** With this option checked, existing Speculative orders within FastReact will not be changed regardless of what the Order import file says.

**Do not change existing "Transit" orders:** With this option checked, existing Transit orders within FastReact will not be changed regardless of what the Order import file says.

**Do not import "Confirmed" orders:** With this option checked, Confirmed orders on the Order import file will not be imported.

**Do not import "Provisional" orders:** With this option checked, Provisional orders on the Order import file will not be imported.

**Do not import "Speculative" orders:** With this option checked, Speculative orders on the Order import file will not be imported.

**Do not import "Transit" orders:** With this option checked, Transit orders on the Order import file will not be imported.

**Days to retain processed import files (0=always):** This value identify how long old imported. processed, files will be kept cor.

**Product mask start and Product mask length:** These values identify that part of the imported Product code that will be used as the base Product from which to copy.

For example:-

- There must be a base Product with a reference of 'ABCD'
- The mask is set to start and length to be 1 and 4.
- This means that whenever you import a NEW Product where the first four characters of its code are 'ABCD' then FastReact will copy the details of this new Product from the exiting Product 'ABCD'. This allows for simpler importing where values such as work content, materials and so on, may be defined within FastReact and then left out of the import file. Any values in the import file will, however, overwrite any values copied from the base Product.

This option must be enabled in the Import options above.

**Do not import orders where delivery is more than " " days old (zero to accept all orders):** This option allows the user to enter an number, to represent the number of delivery days old the order is. If the delivery date of an order in more than "x" days old it will be discounted.

**Purge orders on import - control string (starting after the "where" in a valid select statement:** FastReact can optionally purge a range of orders before import starts. The selection of orders is made though an SQL command which you enter here. The syntax is 'purge from _ORDERS where' followed by the text you type in here. To use this option you will need to understand the SQL language and how to construct queries and you will need to know the structure of the relevant tables in the FastReact database.

Beware that this is a very powerful option and, if not correctly used, could remove more orders than required. Please consult your FastReact supplier for advice.
