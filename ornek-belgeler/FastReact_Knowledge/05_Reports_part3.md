# Main Menu - Reports - Reports (part 3)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports
**Part:** 3 of 3 — sections: Report Layout, Additional report options

---

#### Report Layout

*Context: Main Menu > Reports › Warning › Report configuration › Report Layout*

Once a Report Definition has been created the user will need to tell FastReact how to display the data in the report. This is done through the Report Layout tab on the Reporting dialog.

Initially this tab will be hidden as it is only relevant when a report has been selected and run. After this FastReact will know which report requires laying out and, from the data definition, which fields are available to be displayed.

To get to this tab the user must select the report in the left hand box of the report selection dialog, then click on the label in the centre list box. FastReact will now build the data for the report. When complete the ‘Layout’ tab will be visible. Selecting this tab will open up the Lay out dialog.

**Layout grid:** The layout grid contains information on the formatting of columns and rows in the report. The grid extends 255 columns across (1 to 255) and 10 rows down (A to J). Normally only a small proportion of these cells will be needed to define even a complex report.

Each cell in the layout grid can contain free text that can be typed in, or data from FastReact objects such as orders, products, or formulae with data from a variety of sources. Cells can be formatted with different fonts or different colours which can, if required, respond to different data values in the cells when the report is run.

Each report 'data set' can be displayed in a single report line, or the data can be displayed over a number of report lines, with each line having a different column layout as required.

Reports are configured by clicking the mouse on the cell. Start at the top left and work to the right. FastReact will ignore empty cells but it is better not to leave any as FastReact allows the user to insert new cells between existing cells later if required.

Clicking on the row labels will display additional row specific configuration or on the column header to apply configuration to the whole report. These additional options are described below.

**Cell:** Cells can contain the following data types:

**Free text:** With this option selected the user can enter fixed text into a cell. This allows the user to create row labels which identify each row of a multi row report line.

For example one row might show Planned quantity, the second Product work content and the third the Load as quantity x work content. Without the row labels the report would be difficult to interpret.

**Reference label:** With this option selected FastReact will display and print the internal system reference as the column header.

As an example on a product based report the column header 'Product code' would be replaced with [P.CODE]. This would prove useful when exporting data through the report generator.

**Table label:** This is used in conjunction with the option 'Table cell' and is used to display 2 dimensional data .

For example, you may have different production routes each with different work content for operations. This option allows FastReact to create a table with operations running across the top and routes down the side. The name of the route will appear in this cell which must be immediately to the left of the table data cell. When using this make sure you turn off the repeating field option for this cell.

**Data field:** This option will display on the report the data defined in the cell. The cell can only contain a single valid data reference. This is the most commonly used option. A list of available fields is shown in the list box to the right of the dialog.

See also the description of repeating fields below.

**Formula:** FastReact will select this option automatically if it detects that a cell contains certain characters that are used in mathematical formulae. See the section below on use of Formulae in Reports.

The user can enter formulae and FastReact will attempt to parse them into a value for display in the report. The parsing engine will handle complex formulae up to 250 characters long. Data fields can be dragged from the list box or manually typed formula can be entered into the cell contents box.

**Cell contents:** This field contains the actual contents of the cell. Data fields can be dragged from the list on the right, or typed directly into the field. Dragging is safer as there is less chance of a spelling mistake.

**Field list:** This list contains all of the fields that have been included in the report in the Report Designer above.

> **Note:** Repeating fields have been expanded to show all values as well as the field name. Repeating fields are described in Cell Options below.

**Alignment:** Each cell can be individually aligned to either Left, Right or Centre.

**Column header:** Normally FastReact will insert a column header from its default values. These can be simple text descriptions or dates for certain report fields.

There may be times, however, when the user wants to override the default column headers, this is done by typing in the new column header here.

> **Note:** Column headers are only relevant for the very first row in the cell definition table. Column headers may be up to 10 characters long.

**Width (mm):** This determines the width of a cell when shown in reports. In multi row report layouts cells in different report layout rows can have different widths.

**Precision (dp):** This determines the number of decimal places to be used when displaying floating point numbers. It has no effect on other data types.

##### Cell options

**Lock cell:** Some reports are too wide to fit on a single page and FastReact will spread these reports across as many pages as are needed to accommodate all of the columns. For some reports this may make alignment of the rows difficult and the report is generally less readable. To minimise this problem the user can nominate certain columns to appear on every page of the report. These columns will always appear before normal columns.

**Wrap text:** With this option checked the cell will wrap any text in it.

**Subtotal value:** The user can tell FastReact to subtotal numeric columns. Subtotals will appear where the value in one of the sort columns changes. See Report configuration for more details. This will also work with text in the same column, if the text in the columns are all the same else "?" will appear.

**In subtotal only:** This option only works when Subtotal Value is selected. The user may want only to show the subtotal for a particular column. If this option is selected all rows will be reported but only the subtotal will be displayed, the individual row data will be blanked.

**Repeating field:** Some data fields are classed as a repeating field.

A good example would be a production schedule which runs over several days or weeks. These fields have a ~ as a character in the field name. You will see these listed in the field list as, for example, [S.QTY_WEEK~1], [S.QTY_WEEK~2], [S.QTY_WEEK~3] and so on where the number after the colon indicates the day or week to which the field refers. The field suffixes are automatically generated by FastReact.

In this example, if the user wants to insert a production schedule into a report then they only need to insert the first of these [S.QTY_WEEK~1] and FastReact will recognise this as a repeating field and insert the others for you.

> **Note:** The cell will only contain the one field [S.QTY_WEEK~1] but the cell will be marked as repeating and the report will contain all of the later field values.

There may be occasions when the entire repeating field range is not required, but only one or two selected values. In this case drag the field to the cell contents list as before but then turn off the repeating field check box.

**Repeat first data field only:** In some cases the report may contain a formula which contains 2 repeating fields.

For example, the user may want to multiply the quantity per week [S.QTY_WEEK~1] by the work content for an operation [P.WC~3]. As it stands FastReact would recognise both of these fields as repeating and increment both suffixes. This would result in the quantity for the second week being multiplied by the work content for the 4th operation. If this option is selected then only the suffix for the first data field will be incremented.

**Cumulative values:** This option would take the subtotals and cumulatively add them.

For example, without this option checked the subtotals may run as 10, 20, 30, 40, ….But with this option checked the subtotals would run as 10, 30, 60, 100,….

**Table cell:** If selected then FastReact will create a table within the report.

For example, this could be useful if there are more than one route within a product and the user wants to report all routes for that product.

> **Note:** This option is used in conjunction with the Table label described above.

**Negative in red:** This option is used to tell FastReact to show negative values in red text. Negative values are those which start with a minus sign. FastReact will detect this even if the number is within brackets.

**Format row text:** This option will format the entire row.

**Colour filled cells:** This option is used to tell FastReact to highlight filled cells with a colour of the users choice. This could be a convenient way of marking production schedules on a report where periods with a non zero requirement are not highlighted.

Use the Colour button to select the colour to use. Do not use dark colours as the text would become difficult to read.

**Colour empty cells:** This option is used to tell FastReact to highlight empty cells with a colour of the users choice. This could be used to highlight where essential data is missing. An empty cell is one in which the text is blank or a numeric value is zero.

Use the Colour button to select the colour to use.

**Show cell border:** If selected this option will draw and print a box around a particular group of cells, this may be useful to highlight particular data within the report.

**Show Yes or No:** If selected, then instead of FastReact reporting actual information it will report ‘Yes’ if the cell contains data or ‘No’ If the cell contains no data.

This maybe useful to determine which operations are used for a particular style, instead of reporting the work content.

**Apply exception:** FastReact can produce exception reports that filter out data in specified range. FastReact needs to be told which data fields require to use in this exception filtering.

**Rotate header:** This option will rotate the header from horizontal to vertical.

##### Subtotal

This option allows the user to further define the calculation of the data in a subtotalled cell.

**Sum:** This is the default value and will return a simple addition of data in subtotalled cells.

**Ave:** This will generate an average of cell data. Zero values will be included in this average.

**AveNz:** This will generate an average of cell data. Zero values will not be included in this average.

**Count:** This will return the number of cell values in the subtotal.

**CountNz:** This will return the number of cell values in the subtotal where the cell data is not zero.

**Max:** This will return the maximum value of any cell data.

**Min:** This will return the minimum value of any cell data.

**MinNz:** This will return the minimum value of any cell data where the cell data is not zero.

**Calc:** Special subtotal for formulas to force the formula to be calculated

E.g. If calculating row utilisation (Row Output / Row Capacity) then the subtotal for the group can not be the sum of row utilisation but must be calculated as Sum of Row Output/Sum of Row Capacity.

**Max/Sum:** This is the maximum of the sum.

**Total Calc:** This is used when using the "cell referencing" calculation, fro format of which is {{(A2)}} + {{(A3)}}.

**Count Distinct:** This is a distinct count of all the fields that make up the subtotal.

> **Note:** The subtotal type selected here will follow though to the calculation of Grand total for the whole report. Where a subtotal type of Sum is used the Grand total will be meaningful. It is of questionable value to have a grand total where the subtotal type is not Sum.

**Font (button):** Fonts for individual cells can be specified in FastReact. Only True Type fonts are shown to ensure that the screen preview and the printed page are identical in appearance.

> **Note:** Whilst the user can change the font attributes of any cell, the row height on screen and on the printed page is determined by the font in the very left-hand column. If a larger font is used for subsequent columns there is a danger that the text will be clipped to size.

**Colour (button):** The user can specify a colour for the background to a cell. This colour will be used whether or not the cell contains data. This facility could be used to highlight particular fields in a report where each record is made up of multiple lines on the page.

**Save layout (button):** Click here to save the layout of the report. The report will be rebuilt when the user returns to the Preview tab so that the effect of the changes can be seen. If the layout is not saved the report will not be rebuilt. Right clicking on a report cell will allow the user to perform the following actions:

###### Insert cell

A cell can inserted into a row. All cells, including the clicked cell, will move to the right leaving a blank cell ready for configuration.

###### Delete cell

This will delete a cell from a row. All later cells move to the left to fill the gap. Deleted cells may be pasted into another cell.

###### Cut cell

A cell can be cut, which will place the data onto the clipboard to copy into another cell leaving a blank cell in the previous position.

###### Copy cell

A cell can be copied, which will place the data onto the clipboard to copy into another cell as required. Leaving the original data in place.

###### Cut & Delete cell

A cell can have its contents deleted but you may want to delete the cell from the report as well to move it to another position in the report.

###### Insert & Paste cell

A new cell can be inserted and then data pasted automatically into the table this option is used in conjunction with the Cut & Delete option.

#### Additional report options

*Context: Main Menu > Reports › Warning › Report configuration › Additional report options*

Row specific layout options.

##### Row Height

The user can select the height for each row, FastReact will automatically use the best fit based on the font size you have selected but this can be over-ridden using this option.

##### Rule off

If this option is selected then the user can insert a solid line across the report above and below each cell. Select from the list the style and colour of the line that is required.

##### Other row options

Skip row if all zeros:

For date based reports any rows that have no data within the specified time period will not be displayed.

Unconditionally hide row:

This will always hide a row in a report.

##### Whole report layout options

- Horizontal grid lines: If selected will incorporate horizontal grid lines into the report.
- Vertical Grid Lines: If selected will incorporate vertical grid lines into the report.
- Grid line style: Select from the list of style the format of line you want to use when incorporating grid lines into your report.
- Hide report column header: If selected will not preview or print the column header on the report.
- Hide report icons: If selected this option will not print the report icons on the far left of each line on the report.
- Print Margin: Determines the width of the margin down the left (portrait) or top (landscape) of the printed page.
- Font for column headers and subtotals: This option will enable you to make subtotals row and column header stand out a little more from the normal report font. Chose your required font.

##### Advanced report layouts

There are also advanced reporting options available.

##### Formulae in Reports

The formula parsing engine will handle quite complex formulae. Formulae can contain any mixture of literal values and fields which have been dragged from the field list. The parser will support addition (+) subtraction (-), multiply (\*) and divide (/) as well as nested parentheses and unary minus.

The parser also supports very simple date arithmetic but the date field MUST be first in the formula. If the date is not the first field then the output will be shown as the number of days from 31 Dec 1899. Date calculations other than add/subtract are supported but are probably not logically sound. Subtotals on dates are not supported.

In the following example formulae:

| Symbol | Meaning |
|---|---|
| N | Any normal numerical field name. |
| R | Any repeating numerical field name. |
| D | Any date field name. |
| T | Any text field name. |

Numbers can be used in combination with field names in equations,

e.g. N+1.

The following characters should be used. All equations will be evaluated using the priority rules:

| Priority | Symbol Description |
|---|---|
| 1 | (..) Brackets. |
| 2 | * Multiply. |
| 3 | / Divide. |
| 4 | + Add. |
| 5 | - Subtract. |

If text fields are used in combination with numeric, date or other text fields they are evaluated as '0', so

N+T = N

N\*T = 0

Division by zero is trapped and will return 0 rather than an error.

###### Equation cells will be formatted according to the first field in the cell, so

| N + D | would be formatted as a number. |
|---|---|
| D + N | would be formatted as a date. |
| T + N | would be formatted as text (left aligned by default). |
| N + T | would be formatted as a number. |

###### Equations with dates:

| D + 10 | will return the date plus 10 calendar days. |
|---|---|
| 0 + D1 - D2 | will return the number of calendar days between the date D1 and D2. |
| 10 + D1 | will return the number of days from 31 December 1899 to the date plus 10 days. |

Examples showing how the order of precedence works and how the formulae are parsed

(1+3)\*7+1-8/2 => 4\*7+1-8/2 => 28+1-8/2 => 28+1-4 => 29-4 = 25

1+3\*7+(1-8)/2 => 1+3\*7+(-7)/2 => 1+21-7/2 => 1+21-3.5 => 22-3.5 = 18.5
