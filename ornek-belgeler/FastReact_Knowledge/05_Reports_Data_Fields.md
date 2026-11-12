# Main Menu - Reports - Data Fields

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Reports > Data Fields

---

## Data Fields

*Context: Main Menu > Reports > Data Fields › Data Fields*

This section contains details of the report data fields that are available for creating reports.

Data fields are the basic building blocks for reports and each data field provides access to a specific object in FastReact. Some data fields provide access to a set of data, such as a production schedule or a list of events. These are known as repeating fields.

Data fields are organised into logical Field Groups.

For example there is one for Orders, another for Products and so on.

Some field groups are linked so that if the user can access an order in a report definition then they can always access most of the information about the product for that order as there is a one to one relationship between the Order and the Product (an Order can only have one Product). However, if the report is Product based instead of Order based, then the information will not be available as FastReact cannot be sure that the necessary one to one relationship is valid (a Product may appear on more than one Order)

To help bring some sense to what can and cannot be used in various report designs FastReact offers a number of pre-defined report loops which automatically know which fields in which data groups are logically valid. If an invalid field is chosen then FastReact will raise an error and prevent the use of this field.

We will start with the Report Loops that are available and a description of each:

| Report Loop | Description |
|---|---|
| **Bulked order details** | When " Bulked Orders " is licenced and enabled, this reporting loop will be available to use. This allows for the reporting of Bulk Orders. |
| **By Group and Constraint** | |
| **By Group and Operation** | Allows you to report loading versus capacity in minutes/hours/garments dependant on how the system is set up by factory by operation. |
| **By Operation for all Orders** | Loops though all operations on the order and provides for each operation to appear on it's own row in the report. All data which is accessible with the Order loop is also accessible with this loop. |
| **By Operation for all Strips** | Loops though all operations on the strips and provides for each operation to appear on it's own row in the report. All data which is accessible with the Strip loop is also accessible with this loop. |
| **By Order by Size Down** | Loops through all Orders and sizes and reports ratios and quantities per order down the page. |
| **By Order with Events Across** | Loops through all Orders and gives access to production and development events similar to the above. However, these events are treated as repeating fields and so event data will be displayed in separate columns across the report. |
| **By Order with Events Down** | Loops though all production events for all orders to give access to all fields in the Order, Product and Customer groups. Development events can be included using this loop, but where a Product appears on more than one Order these events will be repeated. This report provides for each event to appear on a separate row down the report. |
| **By Orders by Section Down** | Loops through all orders and sections, such as cutting, sewing etc, and reports daily/weekly quantities per order down the page. |
| **By Plan Row by Product Type** | Loops through each row and reports available product types and efficiencies across the page. This loop reports the efficiency profiles. |
| **By Product with Events Across** | Loops through all products and gives access to development events. However, these events are treated as repeating fields and so event data will be displayed in separate columns across the report. |
| **By Product with Events Down** | Loops though all development events for all products to give access to all fields in the Product group and where appropriate, information on the customer, if any, linked to that product This report provides for each event to appear on a separate row down the report. |
| **By Row and Constraint** | |
| **By Row and Operation** | |
| **Constraint Targets** | |
| **Customer event setup** | |
| **Customers** | Loops through the Customer information in the database. |
| **Delivery** | Because FastReact supports multiple deliveries per order, you cannot use the Order loop to see all delivery information. (The Order loop does provide fields for the first and last delivery so if only 2 deliveries are ever attached to an order then the Order loop will suffice) Like the Order loop, you have access to data in the Product and Customer field groups. |
| **Flows** | Loops through orders and flows and reports positions against the entered flow. |
| **Group Loading by Operation** | Allows you to report loading versus capacity in minutes/hours/garments dependant on how the system is set up by factory by operation but also allows reporting of planned quantities by operation per day/week/month. |
| **Groups** | Loops though each Group in FastReact giving access to data in the Groups field group such as available capacity and loading. |
| **Materials (MRP) by Order** | Loops though all materials for every order giving access to order specific data in the Materials field group such as requirement schedules and shortages. |
| **Materials (MRP) Summary** | Loops though each Material giving access to Material specific data such as stocks and expected deliveries. |
| **Materials Events by Order** | Loops through all events and reports any events that are linked to material items. <br> Order Notes Loops through all the order notes and reports them. |
| **Order Notes** | Loops through all the order notes and reports them. |

*(table continued)*

| Report Loop | Description |
|---|---|
| **Order Schedules** | Loops through Orders and reports daily/weekly/monthly operation schedules. |
| **Order/Product Materials (BoM)** | Loops through Orders and Products and reports the BoM on Orders and/or Products. |
| **Orders** | Loops through every order and gives access to all fields in the Order group (except for production events). Because each order can only have a single product and a single customer all data in these field groups is automatically available, although, as above, development events are not supported in this loop. |
| **Orders by Row** | Loops through then Orders on each row. |
| **Plan Row** | Loops through each row and allows the reporting of row information i.e. Loading capacity, working hours, adjusting hours. |
| **Plan Rows Showing Gaps** | Loops through each row and allows the reporting of row information i.e. Loading capacity, working hours, adjusting hours, as well as Gap information on the Row. |
| **Product Materials (BoM)** | Loops through Products and reports the BoM products. |
| **Product Notes** | Loops through all the Product notes and reports them. |
| **Production Updates** | Loops through all production updates and reports them. |
| **Products** | Loops though all Products and give access to all fields in the Product group (except development events) and, where appropriate, information on the customer, if any, linked to that Product. |
| **Saved Plan 1 v Actual** | Loops though historical data generated by FastReact showing how well you achieved the planned production schedules. This loop replaces the Variance loop. It is used in conjunction with the licence option Save Plan for Variance Reporting. |
| **Saved Plan 2 v Actual** | Loops though historical data generated by FastReact showing how well you achieved the planned production schedules. This loop replaces the Variance loop. It is used in conjunction with the licence option Save Plan for Variance Reporting. |
| **Strip plan by day** | |
| **Strips** | Loops through every strip but skips any that are not planned or are complete. Because each strip must be associated with a single order and delivery most of the fields within the Order, Product, Customer, Row, Group including production and development events, are available This loop provides the best starting place for complex reports or ones that need to pull both production and commercial information together. |
| **Tickets (Shop Floor)** | When Batch Tickets are licenced and enabled, this reporting loop can be used to report these Tickets. |
| **Variance** | Loops though historical data generated by FastReact showing how well you achieved the planned production schedules. |

The following table shows the logical association of the different loops giving an insight into the different data that is available for each loop. Later when we describe each data field we will refer to the short code in the table below to identify which loops are valid for that field.

| Code | Grouping | Available within loops: |
|---|---|---|
| **BPD** | Basic Product Data | Products |
| | | Orders |
| | | Strips |
| | | By Event for all Orders |
| | | By Event for all Products |
| | | By Product with Events Across |
| | | By Order with Events Across |
| | | Variance |
| | | Order deliveries |
| **BPED** | By Product, Events down the page | By Event for all Products |
| **BPEA** | By Product, Events across the page | By Product with Events Across |
| **BOD** | Basic Order Data | Orders |
| | | Order deliveries |
| | | Strips |
| | | By Event for all Orders |
| | | By Order with Events Across |
| | | Materials by Order |
| | | Variance |
| **BOED** | By Order, Events down the page | By Event for all orders |
| **BOEA** | By Order, Events across the page | By Order with Events Across |
| | | Strips |
| **BODO** | By Order delivery only | Order deliveries |
| **BOO** | By Order only | Orders |
| **BOAO** | By Operation for All Orders | By Operation for all Orders |
| **BSO** | By Strip Only | Strips |

*(table continued)*

| Code | Grouping | Available within loops: |
|---|---|---|
| **MBO** | Materials by Order | Materials by Order |
| | | Materials Summary |
| **MS** | Materials Summary | Materials Summary |
| **BGD** | Basic Group Data | Groups |
| | | Variance |
| **GLD** | Group Loading Data | Groups |
| **CD** | Customer Data | Products |
| | | Orders |
| | | Order deliveries |
| | | Strips |
| | | By Event for all Products |
| | | By Product with Events Across |
| | | By Event for All Orders |
| | | By Order with Events Across |
| | | Materials by Order |
| | | Variance |

### Field Groups

*Context: Main Menu > Reports > Data Fields › Data Fields › Field Groups*

The following field groups are available.

- Bulked orders

- Customer
- Designs

- Flow
- General
- Materials
- Material events
- Order
- Plan Group
- Plan Row
- Product
- Strips
- Tickets
- Update
- Variance
