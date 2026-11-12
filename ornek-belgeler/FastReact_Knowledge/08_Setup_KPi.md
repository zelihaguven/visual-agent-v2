# Main Menu - Setup - KPIs - KPIs (Key Performance Indicators)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > KPi
**Index keywords:** KPIs, Performance Indicators

---

## What Are Key Performance Indicators (KPI)

*Context: Main Menu > Setup > KPi › What Are Key Performance Indicators (KPI)*

Key Performance Indicators are quantifiable measurements, agreed to beforehand, that reflect the critical success factors of an organisation. They will differ depending on the organisation. A business may have as one of its Key Performance Indicators the percentage of its income that comes from return customers.

Whatever Key Performance Indicators are selected, they must reflect the organization's goals, they must be key to its success, and they must be quantifiable (measurable). Key Performance Indicators usually are long-term considerations. The definition of what they are and how they are measured do not change often. The goals for a particular Key Performance Indicator may change as the organizations goals change, or as it get closer to achieving a goal.

At present there are four types of KPI in FastReact, each with the ability to track weekly or monthly.

#### On Time Delivery Performance (OTDP), specifically :

*Context: Main Menu > Setup > KPi › What Are Key Performance Indicators (KPI) › On Time Delivery Performance (OTDP), specifically :*

- Total number of orders delivered on time.
- Percentage of orders delivered on time compared to number of planned orders.
- Total order quantity delivered on time (an order may be flagged as late above but it may actually be 90% complete in terms of qty).
- Percentage order quantity delivered on time compared to planned order qty.

#### Cut To Ship (CTS) ratio, specifically :

*Context: Main Menu > Setup > KPi › What Are Key Performance Indicators (KPI) › Cut To Ship (CTS) ratio, specifically :*

- Start operation quantity i.e. order quantity at the cut operation.
- End operation quantity i.e. order quantity at the ship/deliver operation.
- Ratio of the above. Start and end operation can be specified in KPI setup.

#### Overall Lead Time (OLT), specifically :

*Context: Main Menu > Setup > KPi › What Are Key Performance Indicators (KPI) › Overall Lead Time (OLT), specifically :*

- Average number of days between order creation date and last delivered date.
- Min number of days between order creation date and last delivered date.
- Max number of days between order creation date and last delivered date.

#### Work in Progress (WiP)

*Context: Main Menu > Setup > KPi › What Are Key Performance Indicators (KPI) › Work in Progress (WiP)*

- By operation.
- By group.
- By product type.

All these KPIs are displayed on the ProActive desktop with the ability to filter by date, customer and product. Other display options are available here too such as display weekly or monthly and 3D view.

Being part the ProActive desktop means the user can set up multiple windows each with a different KPI in it.

For OTDP, CTS and OLT, clicking on a bar on the graph drills down and displays all order details for that period.

For WiP, the user can choose which operations, groups or product types appear on the graph.

## KPI Configuration

*Context: Main Menu > Setup > KPi › KPI Configuration*

### KPI Config

*Context: Main Menu > Setup > KPi › KPI Configuration › KPI Config*

**WiP Operations:** This is a list of all the operations that have been set up in the system. Each operation can be chosen can be enabled so the it can be displayed on the Pro-Active Desktop.

#### Start and Delivery Operations

*Context: Main Menu > Setup > KPi › KPI Configuration › KPI Config › Start and Delivery Operations*

**Start:** This is the start operation.

**Delivery:** This is the operation that marks the delivery.

**Allow manual updates:** This option allows the user to use manual updates.

**Disable forward KPIs:** This option disables forward looking KPIs.

**Save (button):** This button will save the selections made on this dialog.

### KPI Selection

*Context: Main Menu > Setup > KPi › KPI Configuration › KPI Selection*

#### Disable the following KPIs

*Context: Main Menu > Setup > KPi › KPI Configuration › KPI Selection › Disable the following KPIs*

This is a list of selectable options that can have their KPIs 'turned off'.

**On time delivery performance:** This option will disable the On time delivery performance KPI.

**Cut to ship:** This option will disable the Cut to ship KPI.

**Overall lead time:** This option will disable the Overall lead time KPI.

**Work in progress:** This option will disable the Work in progress KPI.

**Save (button):** This button will save the selections made on this dialog.

### Initial setup

*Context: Main Menu > Setup > KPi › KPI Configuration › Initial setup*

#### Update KPI data

*Context: Main Menu > Setup > KPi › KPI Configuration › Initial setup › Update KPI data*

**Update Order Nos:** This is a user entered list of all the orders in the FastReact system which will either be entered into or deleted from the KPI Historical data table.

##### Update Type

**SQL:** This selection will force FastReact to use data from a SQL table.

**Memory:** This selection will force FastReact to use data from the FastReact memory.

##### Operation Type

**Insert:** This will insert the required Order numbers into the data table.

**Delete:** This will delete the required Order numbers into the data table.

##### KPI Type

**Standard:** This is the basic order data KPI.

**WiP:** This is the WiP data KPI

**Forward:** This option will produce a projection based upon current data.

**Go (button):** This button will update the KPI with the above selections.

#### Generate KPI

*Context: Main Menu > Setup > KPi › KPI Configuration › Initial setup › Generate KPI*

##### KPI

**On time delivery performance:** This option will produce a KPI based upon the 'time delivery performance.'

**Cut to ship ratio:** This option will produce a KPI based upon the 'cut to ship.'

**Overall lead time:** This option will produce a KPI based upon the 'overall lead time.'

##### Aggregate Period

**Weekly:** This option will set the period to weekly.

**Monthly:** This option will set the period to monthly.

**Generate KPI (button):** This button will create the KPI in the dialog below.

#### Filters

*Context: Main Menu > Setup > KPi › KPI Configuration › Initial setup › Filters*

**Customer:** The KPIs can be filtered by Customer.

**Product:** The KPIs can be filtered by Product.

Dates can be set over which to view these filters.
