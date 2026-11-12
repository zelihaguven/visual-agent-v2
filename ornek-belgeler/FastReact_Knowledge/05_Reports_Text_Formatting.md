# Main Menu - Reports - Text Formatting

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports > Text Formatting

---

## Text Formatting

### Advanced Formula Options within Reporting Fields

| Function | Description | Example |
|---|---|---|
| @SELECT | Reports user defined text based on selected fields and formulas in cell. | @SELECT([O.DAYS_LATE]:<0:URGENT,OK) <br> The example above will enter ' Urgent ' in the report field if the order days late for delivery is < 1 if >1 then it enters ' OK' . |
| @SELECTNUM | Reports a user defined number based on selected fields and formulas in cell. | @SELECTNUM([O.DAYS_LATE]:<0:1,0) <br> The example above will enter 1 in the report field if the order days late for delivery is < 1 if >1 then it enters 0. |
| @SELECTDATE | Reports a specific date based on selected fields and formulas in cell | @SELECTDATE([O.EVENTS_DONE~8]:>0:[O.EVENTS_DONE~8],[O.EVENTS_TARGET~8]) <br> Will report the completed date of an event if there is one, otherwise the target date will be reported. |
| | Colouring text in reports. | Must be first cell in report layout <br> @SELECT([P.PRODTYPE]:SHIRT:@SELECT([O.CUST]:riders:>RED>BOLD>ITALIC,>BLACK),>BLACK) <br> The result of this will colour up the row text in red bold italic if the product type = Shirt and customer = Riders if not then row text will be black. |
| | Colouring text in reports. | Must be first cell in report layout <br> If no criteria is required when colouring up report lines then you can simply use >Red,>Bold and this will colour the text in the row in the selected colour |
