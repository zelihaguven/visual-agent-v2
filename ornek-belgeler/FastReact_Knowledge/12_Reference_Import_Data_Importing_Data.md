# Reference - Importing Data - General

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Importing Data
**Index keywords:** HDR, Import Header Files

---

This section contains some general information on importing data into FastReact.

See below for information on specific import files.

## Introduction

*Context: Reference > Import Data > Importing Data › Introduction*

Data can be imported into FastReact in a number different ways. The recommended approach is through simple text files formatted as tab separated variables (\*.txt) or comma separated variables (\*.csv). These have the advantage of being fairly simple to construct, easy to debug and fast. Each of the objects (Orders, Products etc) in FastReact are imported in separate files, although in some cases more than one file may be needed to for all information for an object

FastReact also has the capabilities of taking data in a variety of different formats and converting these to the format expected by the import routine. See Pre-processing.

### File names and locations

*Context: Reference > Import Data > Importing Data › Introduction › File names and locations*

The file names are specific to the data being imported but all files must be placed into the directory specified for import files. See the Setup/Configure/General menu option.

It is essential that the workstation that performs the import has full create/read/write/delete access rights to this directory.

FastReact will rename the import file before processing by adding an underscore character to the beginning of the file name. This minimises the chances of the host system writing to the file while FastReact is reading it.

### Field names

*Context: Reference > Import Data > Importing Data › Introduction › Field names*

FastReact expects the import files to contain field names (headers) that it recognises. Certain fields will be essential whilst others may be omitted. If an essential field is missing or invalid then the file being processed will be aborted and a fatal error will terminate the import process.

## Compliant Field names

*Context: Reference > Import Data > Importing Data › Compliant Field names*

Many tools used to create import files will only allow alpha-numeric characters in the field names whereas FastReact will allow a wider variety of characters to be used. For this reason you should use the following conversion when building import files. The 'Use compliant import file field names' option under the import configuration menu option must also be ticked.

| Value in Fast React | Compliant value |
|---|---|
| **.** | **1** |
| **^** | **2** |
| **~** | **3** |
| **:** | **4** |

### Repeated fields

*Context: Reference > Import Data > Importing Data › Compliant Field names › Repeated fields*

FastReact can import repeating data under a common field name.

An example would be the work content for different Operations on a Product. FastReact can accept values for any number of Operations. In this case the field names are P^WC:n to P^WC:m where 'n' and 'm' are the Operation external reference numbers appended to the field header with a colon as a separator character.

### Field types

*Context: Reference > Import Data > Importing Data › Compliant Field names › Field types*

FastReact can import the following data types.

**Text:** Simple text with a length up to the limit shown. Any characters beyond this length will be truncated. FastReact will convert text to upper case where necessary.

**Integer:** Numeric values with no floating point element,

i.e. they must be a whole number.

Fields can be padded with spaces or zeros to the left of the number if required.

**Float:** Numeric values with a floating point element. FastReact will import data to the precision you specify in the import file but normally will not display more than 3 places of decimal.

**Date:** Dates can be imported in one of several date formats as specified the import configuration menu option. These are independent of the International settings in Windows to maintain import data integrity irrespective of the settings on the workstation.

### Data field format

*Context: Reference > Import Data > Importing Data › Compliant Field names › Data field format*

This section only applies to CSV files.

Fields are delimited by commas so that FastReact can work out which data relates to each column in the file. There may be times when a comma on its own will be insufficient to delimit the field and this can cause the import routine in FastReact to fail.

A good example would be a text field where the user has entered a comma in the text data. This is quite valid from a user point of view but may confuse the import routine resulting in the field being split into two. To avoid this situation all Text fields must be delimited by quote marks as well. It is not bad practice to surround all fields with quotes.

For example,'1234.00','ABC,XYZ','FastReact'

In this example the comma between the ABC and the XYZ would cause the import routine to parse this as 4 fields instead of 3. The quote marks prevent this error.

> **Note:** Using tab separated files avoids this problem as tabs are rarely used in text fields.

## Import Header Files

*Context: Reference > Import Data > Importing Data › Import Header Files*

In some scenarios imports files being generated from a clients Business System will be unable to provide the required field headers on the CSV or TXT files. To help with this separate HDR files can be created containing the field headers in the same format as the Business System generated data files. These files are saved in the same location as the defined import. For example, if the Business System creates a CSV data file for FastReact to import then the associated HDR file must also be created in CSV format and then renamed to be a .HDR file.

This requires that the option. "Add field headers from separate header file," to be enabled.

> **Note:** CSV import files must have a Header file created in CSV and TXT import files must have a Header file created in TXT. These cannot be mixed.
