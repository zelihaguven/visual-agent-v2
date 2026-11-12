# Main Menu - Customers - Add and Amend

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Customers > Add and Amend
**Index keywords:** Add, Customer

---

## Customers - Add/Amend

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend*

### Define

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend › Define*

**Enter customer name:** Enter the name or code of the customer.

#### General

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend › Define › General*

**Description:** This field can hold a brief description of the customer. This field can be used for the real customer name and a short customer code entered into the Enter customer name field. This would allow, for example, different customer references for different customer divisions, delivery locations or even individual stores, but have a common description across all of these. The description can then be used in reports.

**Customer priority (0..255):** This is only used in the optional APS function.

**Delivery location:** Select a delivery location from the list. Delivery locations are defined during transport set-up. Choose the default delivery location for orders to this customer. However, the delivery location can be changed on an order by order basis for any customer. The 'Delivery location' is used by FastReact to determine the transport days from manufacturing site to that location.

**Distribution centre:** Select a group to act as a distribution centre for this customer or leave this entry as (none) if the delivery will be delivered directly to this customer.

FastReact will take account of transport into and out of the DC and can also make allowances for any operations that need to be carried out at the DC, such as pressing and final packing.

**Demand offset (plan line):** This demand offset is used in conjunction with MPS.

**Customer group:** Select a customer group from the drop down list. This will assign the customer to that customer group.

**Seriously late after:** FastReact warns of late deliveries by changing the colour of the strips on the planning board. The value entered here determines the point at which an order changes from 'just late' to 'very late'.

**Planning colour (button):** This button will allow the selection or modification of the colour of the strips for this customer. Depending on the selected view of the planning board, all orders for the customer will appear with this colour allowing quick and easy identification.

**Insert / Update (button):** This button will insert or update the customer.

**Delete (button):** This button will delete the customer.

### Rename

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend › Rename*

You can rename a customer at any time without creating data integrity problems.

**Select a customer to rename:** Select a customer from the drop down list to rename.

**Enter a new name:** Enter the new customer name.

**Rename:** This button will rename the customer.

### Events

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend › Events*

This tab is used to select the events that are required for orders linked to this Customer. This maybe useful if you have a lot of events in your event framework but not all these events are required for every Customer.

**Select customer:** Select a Customer from the list.

**Production or Development:** Select the required event type, production or development, that will be viewed in the table below.

##### Event table

This shows a list of all events previously set up in the Event framework.

**Normal User:** This shows the person normally responsible for each as you have defined in the event framework.

**Alias user:** You can tell FastReact that the person responsible for orders/products for this customer will not be the 'Normal' user shown. You can select another user by dragging them from the list on the right. This will override the user you may have defined in any critical path timetable or the event framework. This allows different users to be responsible for any event for each customer.

**Enabled:** FastReact will consider these events as required for this Customer, however certain events may be required only under unusual circumstances. Events can be disabled for specific customers.

**Report:** You can define certain events to go into reports and others to be omitted. This allows you to define a set of most critical events to be reported and monitored. Most reports, however, will include all events irrespective of this setting.

**List of users:** Users can be dragged from this list (with the mouse) into the Alias user column.

**Update (button):** This button will insert or update the customer.

### Customer Group

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend › Customer Group*

This tab is used to create, delete and rename Customer Groups.

**Add customer group:** Add the name or code of the customer group.

**Save (button):** This button will save the group.

**Delete customer group:** A group can be selected and deleted from the group list.

**Delete (button):** This button will delete the selected group.

**Rename customer group:** Select a group from the drop down list to rename.

**New group name:** Enter the new group name.

**Rename (button):** This button will rename the selected group.

### User defined fields

*Context: Main Menu > Customers > Add and Amend › Customers - Add/Amend › User defined fields*

It is possible to configure which UDFs will be visible for a Customer. On this tab it is possible to select a Customer and a UDF type. Once these are selected, a list of currently visible UDFs is shown along with any other available UDFs that are currently hidden/excluded. Currently, all UDFs are visible by default. UDFs can be moved from one list to the other. If a UDF is not visible, it is added to the database as an Excluded UDF for this customer.

**Select a UDF type:** This is a list of all the defined UDFs the is system.

**Visible UDFs:** This is a list of all the visible UDFs the is system that are visible to the selected Customer.

**Available UDFs:** This is a list of all the available UDFs the is system that are visible to the selected Customer.

**Update (button):** This button will update the Customer UDFs.
