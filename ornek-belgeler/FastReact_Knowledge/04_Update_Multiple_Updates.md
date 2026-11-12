# Main Menu - Update - Multiple Updates

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Update > Multiple Updates
**Index keywords:** Multiple Update

---

## Multiple Updates

*Context: Main Menu > Update > Multiple Updates › Multiple Updates*

FastReact allows the user to do batch updates based upon:

- Orders
- Products
- Materials

This allows the user to change certain criteria on all Orders/Products/Materials in the system in one go.

### Multiple updates

*Context: Main Menu > Update > Multiple Updates › Multiple Updates › Multiple updates*

**Select a previously saved profile:** From the drop down list a previously saved profile can be selected.

**What items do you want to update:** Highlight the item(s), from the predefined list, which require an update. This list consists of orders, products and materials.

**What value do you want to change:** Upon selecting the item that requires updating, this list box will be populated with values relating to the selected item. These values are what will be changed upon updating. These values can be in the form of events, User Defined values order/product/material values.

**How do you want to link these items:** Upon highlighting the 'value to change', this list will populate with values that will link the 'item' with the 'value to change'.

**Link value (wild cards allowed):** This field is for filtering the details about the current value that has to be changed. Wild cards can be used in the field.

For example, 'W\*' will filter all records that start with 'W'.

**Count (button):** This returns the number of records to be changed with relation to the above criteria.

**Select (button):** This button, upon the completion of the above fields, when clicked, will bring up an update dialog from which can be chosen the group of orders, products or materials that will be updated.

The headings below all relate to the text box below the Check count. The heading for which will change depending upon the criteria set in the previous steps.

#### For order items to be updated.

*Context: Main Menu > Update > Multiple Updates › Multiple Updates › Multiple updates › For order items to be updated.*

**Mark complete - Enter 1 to complete or 0 to clear:** These options will either complete(1) (the order for example) or clear (0) the check box.

**Confirm Suggested order - Enter 1 to confirm:** This option will mark the selected Suggested Order(s) as Confirmed when a "1" is entered in the text box.

**Change order status - Enter C/P//S/T:** This option will either set the order status to Confirmed, Provisional, Speculative or Transit.

**Change extended order status - Select new status:** This option will set the Extended order status for the selected orders. The Extended order status is selected from the drop down list.

**Delete order - Enter 1 to confirm deletion:** This option will delete the selected orders when "1" is entered in the text field.

**Add user note - Enter note text:** This option will enter a Order note to the selected orders.

**Plan in group - Select new group:** This option will set the Plan in Group field on the selected Orders via the drop down list.

**Set Transport Method - Select transport method:** This option will set the transport method on the selected Orders via the drop down list.

**Apply Reservation - Select material reservation:** This option will set the material reservation field on the selected Orders via the drop down list.

**Update order efficiency - Enter a value between 0 and 100:** This option will set the order efficiency on the select Orders.

**Retain target dates - Enter 1 to retain (will not overwrite existing):** This option will Retain the target dates when a "1" is entered in the text field.

**Retain current target dates - Enter 1 to save current targets:** This option will Retain the current target dates when a "1" is entered in the text field.

**Update order event base date - Enter a valid date (dd/mm/yyyy):** This option will set the Order Event Base Date to the selected date..

**Change timetable - Select a timetable:** This option will set the timetable on the selected Orders via the drop down list.

**UDF - Enter Text up to 15 characters:** This option will allow the input of UDF text.

**Order financial values - Enter a numeric number:** Enter a numeric number.

**Order event complete/skipped dates - Enter a valid date:** A valid date can be entered. This field will be used mainly with the updating of events.

**Operation standing time - Enter positive standing time or 0 to clear:** A positive number can be entered.

#### For product items to be updated.

*Context: Main Menu > Update > Multiple Updates › Multiple Updates › Multiple updates › For product items to be updated.*

**Stock policy weeks - Enter number of weeks (numeric):** Enter a number of weeks.

**Min and incremental order quantity - Enter minimum quantity (integer):** Enter a minimum quantity in the form of an integer.

**Change plan line demand rule - MFC FO CO CONZF TFC:** This option will change the demand rule when the correct rule is entered in the text field.

**UDF - Enter Text up to 15 characters:** This option will allow the input of text.

**Product financial values - Enter a numeric number:** Enter a numeric number.

**Product event complete/skipped dates - Enter a valid date:** A valid date can be entered. This field will be used mainly with the updating of events

#### For material items to be updated.

*Context: Main Menu > Update > Multiple Updates › Multiple Updates › Multiple updates › For material items to be updated.*

**Purchase lead time days - Enter number days (numeric):** Enter a number of days.

**Call off lead time days - Enter number days (numeric):** Enter a number of days.

**Non phased material - Enter 1 to for Phased or 0 to not Phased:** These options will either set the material to phased (1) or non phased (0).

**Non critical material - Enter 1 to for Critical or 0 to not Critical:** These options will either set the material to critical (1) or non critical (0).

**UDF - Enter Text up to 15 characters:** This option will allow the input of text.

**Update (button):** This button will update the selected orders, products or materials with the required change.

**Clear (button):** This button will clear the dialog ready for the next Multiple Update.

**Save profile (button):** This button will save the update scenario so that it can be used in the future. The profile requires a name which will be available in the 'Select a previously saved profile' drop down list.

**Delete profile (button):** This button will delete the currently displayed profile.
