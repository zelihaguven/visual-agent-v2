# Reference - Importing Data - File Pre-processing - Conversion

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Pre-Processing > Conversion
**Index keywords:** Conversion, File Pre, Processing

---

The file has a header section with the following entries all of which are required. Each of these is described below.

| [Common] | Section Header |
|---|---|
| **PreProcess** | Convert <br> This can be omitted from the conversion type configuration files as conversion is the default process. |
| **FileType** | Specifies the format of your input data file. This can be TAB , for tab separated, CSV for Comma separated variable, DBF for Dbase file, XLS for Microsoft Excel files, or FW for fixed column width files. Other values would identify a single character as the separator. <br> For example, you could use ‘ \| ’ or ‘ ~ ’ as a separator. |
| **OutputFileType** | Specifies the format of your output data file. This can be TAB , for tab separated or CSV for Comma separated variable. |
| **SkipLines** | This tells FastReact to ignore this number of lines at the top of the file. This allows header data to be ignored. |
| **DataLines** | This tells FastReact how many lines in the your file are used to represent a single data item. There is a maximum of 10 lines in the file for each data item. |
| **InputFile** | This is the name of the file to be converted. FastReact will change the file name by adding an underscore to the name before processing. Do not use one of the standard FastReact import file names. If the input type is XLS then a comma followed by a sheet name can be added to the file name to specify a particular sheet in the workbook. If no sheet name is added then the first sheet is used. |
| **OutputFile** | This is the name of the file that FastReact will import. The name must be one of the standard names that FastReact expects. The output file will always be the format specified in OutputFileType . See above. |
| **Append** | Set this to ' Y ' if you want FastReact to add the contents of this input file to the specified output file. This will allow several input files to be added together into a single FastReact output file. Normally the output file will be emptied before adding the contents of the input file. |
| **DateFixUp** | This allows dates to be converted to a week or month ending date. Valid settings are ' WE ' and ' ME '. Any other value will be treated as no date adjustment. |
| **FieldCount** | The number of field descriptions as listed below. Field descriptions must be repeated FieldCount times. |
| **HeaderLines** | This specifies the number of line from the start of the file, after SkipLines , that will be read in and can be accessed and used in the output. |
| **Repeat** | This value is used to control how many times the output will be repeated. This defaults to 1 if not set. |
| **RowToColField** | This specifies the field (e.g. =F1, =F2) that is used to control when a new output row starts. ( BZ4195 ) |
| **RowToColCount** | This is the maximum number of rows/columns for each RowToColField . This number of columns will be output for each field being converted, regardless of how many rows there are - all fields not required will be blank. (BZ4195) |
| **ExcelFullExtent** | This can be set to =1 to force the extent of each sheet to be determined by Excel. It can be omitted or set to =0 to revert to the default method of looking where the continuous data in the first row and column end. |
| **[Fn]** | The field header identifier. This must be in the format of [Fn] where ' n ' is a sequential number starting from 1. |
| **Code** | This is the FastReact field code to be added to the processed output file. This must be a valid FastReact code. If the code is blank then the field will not be added to the output file. This can be useful if the value is being added to something else using Add. |
| **Line** | The line in the text file on which the data to be extracted is located. This only has relevance if the input file has multiple data lines for each data item. Normally this will be set to 1. |
| **Offset** | This is the data entry in the import file. For TAB and CSV files this will be the column number (starting from 1). For Fixed Width files this will be the number of characters into the line (starting from 1). |
| **Length** | For Fixed Width files this is the number of characters to extract for this data entry. This value has no relevance for TAB or CSV files and will be ignored. |
| **Part** | FastReact can get part of a value. The part must be entered in the format ' a,b '. " a " can either be ' L ' (left), ' R ' (right) or a number representing the character of the value to start from. ' b' is the number of characters required. |
| **Add** | FastReact can combine entries in the input file into a single output field. The value must be a valid field header identifier ( i.e. Fn ) as defined above. FastReact can add together data from multiple fields but be careful not to create a circular reference. <br> For example, you could add together the Product code, Delivery date and Colour to derive an Order reference for FastReact. |
| **Separator** | This is only used when adding values using Add. The default separator when adding fields is " :: " but a different separator can be used if required. |
| **Constant** | This specifies a hard coded field value. This can be text, a number or a date. |
| **Lookup** | This is the name of the lookup to use from the importpp.ini . The value, after Part and Add, can be looked up in a list and an alternative value used. <br> For example, the user can lookup the first character of the product code to find the product type . |

*(table continued)*

| [Common] | Section Header |
|---|---|
| **Calc=ShowError** | FastReact will try to evaluate the result. <br> For example, if a field result is " 7*2 " then FastReact should add 14 to the output file. (N.B. The result value "7*2" could be created by adding two fields with the " * " as a separator). <br> Other possible values for ' calc= ' :- ' Off ' - ' No calculation ' - ' ZeroError ' – if an error occurs the error is not displayed and a ' 0 ' is used as the result.- ' BlankError' – If an error occurs the error is not displayed and an empty string is used as the result. |
| **RepeatNumber** | This is used to control when a field is output based on the Repeat number above. If no value is set then the field will appear for all lines. <br> Note: <br> If using repeats then there MUST be a field for each possible repeat value so that the correct number of columns are added to the output file. |
| **HeaderField** | This can be set to =1 for any fields where the output values should come from the header lines (as above) rather than the data lines currently being processed and can be omitted or set to =0 for all other fields. |
| **IgnoreLineIfBlank** | This can be set to =1 for any field and will cause the entire output line to be omitted if the value of the field is blank. It can be omitted or set to =0 for all other fields. |
| **AddRepeatToOffset** | This is used in conjunction with the Repeat functionality which allow input lines to be processed and output multiple times applying different rules for each output. This can be set to =1 for any field and will cause the repeat offset specified for the field to be adjusted by the number of the current repeat. This allows for different sequential columns to be read for each repeat. For the first repeat the specified offset wont be adjusted, for the second repeat the offset will be incriminated by 1, etc. <br> This can be omitted or set to =0 for all other fields. |
| **TransformDate** | This is used to convert a date in one format to a date in another format and can also adjust the date to begin/end of week/month. It can have 2 or 3 parts with commas between for input format, output format and optionally the adjustment type. Adjustment types are a 2 character code of mb (month beginning), me (month end), wb (week beginning) or we (week end). <br> For example, TransformDate=yyyymmdd,dd/mm/yyyy,me <br> This has been extended to allow for an additional adjustment code of ADJ= to allow the input date to be adjusted by a fixed number of days. <br> For example, TransformDate=yyyymmdd,dd/mm/yyyy,ADJ=-7 |
| **RowToCol** | This must be set to =1 for any fields being converted from rows to columna and can be omitted or set to =0 for all other fields. Converted columns Headers will be output with a sequential number suffix. (BZ4195) |
| **TotalCode** | This can optionally be set for any field being converted from Rows to columns and will cause the column heading specified to be added to the output rows with sum of the values for that feed. (BZ4195) |
| **Decimals** | When the ‘Decimals’ option is specified against a field, the output value of that field should attempted to be converted into a number. If this conversion succeeds, the number can be rounded to the required precision. If the conversion fails, an error must be thrown warning the user that the value cannot be rounded as it is not a number. <br> This is limited to numeric fields only and the max decimal place is 6 . (BZ13986) |

## Advanced preprocessing

*Context: Reference > Import Data > Pre-Processing > Conversion › Advanced preprocessing*

There are a number of additional preprocessing options that can be applied.

### Date fix up

*Context: Reference > Import Data > Pre-Processing > Conversion › Advanced preprocessing › Date fix up*

This option allows the user to convert dates in the input file to week ending or month ending dates. This allows for consistency of dates.

For example all delivery dates to be week ending dates rather than spread throughout the week. To enable this function all that is needed is to put DateFixUp=WE (or ME) against the date that the user wants adjusted.

Some caution however, might need if the user is using this option combined with the Add function above. This can be used to create a FastReact Order code as a combination of product reference and delivery date. In the input file there may be several requirements for a product on different delivery dates within one week. After date fix up these will all be adjusted to the same date and this would essentially result in FastReact orders being overwritten.

### Creating multiple orders

*Context: Reference > Import Data > Pre-Processing > Conversion › Advanced preprocessing › Creating multiple orders*

In some circumstances it can be useful to create multiple FastReact orders from a single order in the input file.

For example, the input file contains forecasts for monthly periods but you want FastReact to plan orders based on weekly delivery dates.

To achieve this the user only needs to tell FastReact which field contains the original delivery date and delivery quantity and which field contains the base order reference. FastReact will then create new orders each with the base order reference. The user must use the Add function above to append the new weekly, delivery date to create a unique order reference.

Orders for calendar or financial month periods will be split into weekly divisions, based on the number of your planning week ending dates in the period. Thus some orders may be split into 4 weeks, others in to 5 weekly deliveries.

The following field qualifiers must be used SDC_ORDER (or SDF_ORDER) for the order reference SDC_DATE (or SDF_DATE) for the delivery date SDC_QTY (or SDF_QTY)

 for the delivery quantity.

The qualifiers beginning with SDC are for calendar months whilst SDF are for financial periods.

> **Note:** To use the latter it is essential that the financial calendars in FastReact are correctly set up and maintained.
