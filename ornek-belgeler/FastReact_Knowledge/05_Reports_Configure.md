# Main Menu - Reports - Configure

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports > Configure

---

## Configure

A brief description of the icons available for each field in the Configure report screen.

### Sort

| | No sorting | The field will not affect the sort order of the report. |
|---|---|---|
| [Screenshot: Report Filter A to Z] | Sort ascending | The report will be sorted in ascending order (a..z) by this field. |
| [Screenshot: Report Filter Z to A] | Sort descending | The report will be sorted in descending order (z..a) by this field. |
| [Screenshot: Report Filter Flow Sort] | Flow sort | The report will be sorted in a user specified sequence. |
| Warning: If the report is being sorted and or subtotalled via the flow, then this Sort function MUST be used rather than the traditional A to Z sorting. | | |

### Subtotal

| | No subtotalling | The field will not affect the subtotalling of the report. |
|---|---|---|
| [Screenshot: Report Filter subtotal] | Subtotal | When the value of a field changes a subtotal will appear in the report. This option is only applicable to sorted fields. |
| [Screenshot: Report Filter sub subtotal] | Split subtotal | When a subtotal appears in the report it can be split between the values indicated by this field. The original purpose of this option was for flow reporting so that the various flow types indicated by the flow filter could be seen in the report subtotal, but it can be used in other scenarios. <br> For example, a simple order list can be subtotalled by customer, but have that subtotal split between products. This option is only applicable if you have subtotals in the report. <br> Nested subtotals can be achieved by selecting multiple subtotal fields. The report will be subtotalled the earliest field and by later fields within that. The rows in the grid can be dragged up/down to change the subtotal nesting order. |
| [Icon: report sub break] | Subtotal break | This causes subsequent subtotals to be added where either the subtotalled value itself changes – or the ‘Subtotal break’ value has changed – but without displaying a separate subtotal at the ‘Subtotal break’ level. <br> For example: <br> [Screenshot: report sub break] |

### Page

| | No page break | Page breaks will just occur naturally when a page is full. |
|---|---|---|
| [Screenshot: Report Page break] | Force page break | Page breaks will occur when the value of this field changes, after any required subtotals have been printed. This option is only applicable to sorted/subtotalled fields. |

### (Filter) Type

| | Include | Only rows where the field value is in the ‘ Filter from ’ – ‘ Filter to ’ range, or where the field value matches the ‘Filter from’ (including wild-cards) will be included in the report. |
|---|---|---|
| [Screenshot: Report Not include] | Exclude | Rows where the field value is in the ‘ Filter from ’ – ‘ Filter to ’ range, or where the field value matches the ‘ Filter from ’ (including wild-cards) will be excluded from the report. |
| [Screenshot: Report multiple include] | Inclusive list include | Only rows where the field value is in the list in ‘ Filter from ’ will be included in the report. <br> This option was developed for flow reporting so that only certain flow types indicated by the flow filter would be seen in the report. <br> For example a filter of ‘ <pln><rev> ’ could be used to just see ‘Planned flow’ and 'Revised flow’ in the report. |
| [Screenshot: Report multiple exclude] | Multiple Exclude | Rows where the field value is in the list in ‘ Filter from ’ will be excluded in the report. Such as shirts* pants, this is limited to 15 characters. |
| [Screenshot: Report Filter equals] | Exact Include | Ability to show exact data from the multi select filter. Along with the Exact Include icon, ‘ [*] ’ square brackets are used to define the data included in the filter. For example, Filtering for “Bobbie”will also show “Bob”, however using the filter, Exact Include , the user can filter for [Bobbie] and have only Bobbie displayed in the report. |
