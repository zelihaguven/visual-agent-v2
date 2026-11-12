# Reference - Exporting - Exporting Data

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Exporting Data
**Index keywords:** Exporting Data, Exports

---

## Exporting Data

FastReact can export data in a flexible and simple manner. Data is exported in the form of text files with columns delimited by Tabs or by Commas. Data can be exported on demand or on a timed schedule or both.

The export mechanism is driven through the Report generator and so will have access to all of the FastReact data, even if this data is calculated 'on the fly' and only available at run time.

Exported data reflects the filters used in the report configuration so that the exported file only contains data that appears in the report. Likewise the report layout is also considered so that data that is not displayed can be excluded. This is controlled by a flag setting in Main Menu - Setup - Configure - General on the Export tab.

Two different formats are supported:-

### Simple format

This is the default format and is ideally suited to extracting data from FastReact and importing into a spreadsheet for any further manipulation.

For example:-

| O.CODE | P.CODE | 01/02/2003 | 02/02/2003 | 03/02/2003 |
|---|---|---|---|---|
| Order 1 | Product A | 100 | 120 | 130 |
| Order 2 | Product B | 60 | 60 | 60 |

### Normalised format

This optional format is best suited to providing import data for another application. Where an export is normalised any data that would repeat across multiple columns will appear in the output file each on its own row.

For example:-

| F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|
| Order 1 | Product A | S.QTYDAY | 01/02/2003 | 100 |
| Order 1 | Product A | S.QTYDAY | 02/02/2003 | 120 |
| Order 1 | Product A | S.QTYDAY | 03/02/2003 | 130 |
| Order 2 | Product B | S.QTYDAY | 01/02/2003 | 60 |
| Order 2 | Product B | S.QTYDAY | 02/02/2003 | 60 |
| Order 2 | Product B | S.QTYDAY | 03/02/2003 | 60 |

In this case the table shows 2 orders and the planned quantity per day for each. Compare this with the layout in the Simple format above.

> **Note:** When setting up the data to go into this type of export it is essential that all repeating data be placed AFTER any non repeating data. If this rule is not observed then the output file may be badly formatted.

Field names are always 'F1' to 'Fn' where 'n' is the number of columns in the table.

Data in the tables is of type string irrespective of the underlying data type. This allows for more flexibility in the contents of the table, allowing for instance, different table rows to contain different data types.

Table names which include an underscore are not allowed. This will prevent users from overwriting a FastReact system table as all of these start with an underscore.
