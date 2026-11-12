# Main Menu - Setup - Configure - Production

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > Production

---

## Configure Production Options

*Context: Main Menu > Setup > Configure > Production › Configure Production Options*

**Update (button):** This button will update any changes.

### Start up

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Start up*

#### Build up curves

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Start up › Build up curves*

**Build up curve enabled:** When this is enabled FastReact will allow the configuration of a number of Build up allowances to link to Orders on the planning board.

**Smoothed build up:** When enabled a smooth build up curve will be used. This is only relevant where the build up period (see below) is more than 1 day.

For example, with an efficiency of 20% on day 2 and 40% on day 4 (period = 2 days) then a smoothed build up would give an efficiency of 30% on day 3 whilst with no smoothing the efficiency would remain at 20% until day 4.

Smoothing gives more accurate results but is harder to verify that the results are correct.

**Cap to maximum build percentage:** When enabled this option will allow the planned to cap the build up at the maximum build percentage as defined on the Build up curve dialog.

**Automatic build up insertion:** When enabled the you can set up a pre-defined matrix of build curves. These build up curves will be inserted between strips on the planning board automatically based on the product types of the relevant strips.

For example, going from a T-Shirt to a Jacket may require a build up curve type 1 (50%-70%-90%) whilst going from a Jacket to a Trouser may require a build up curve Type 2 (70%-75%-85%-90%).

**Clear build up when moving strips to a new row:** When enabled this option resets the build up for the moved strip and the build up will have to start from the beginning again.

**Retain strip follow on status when moving to a new row:** By default when a strip with a follow on is moved to another row it looses its follow on status. However, with this option enabled that status can be retained.

**Period (days):** A time period can be specified for each step of the build up curve. Enter the time increment in working days between successive steps in the build up curve.

#### Change allowances

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Start up › Change allowances*

This section enables the configure with the way that FastReact uses change time (e.g. machine down time between different products) within FastReact.

**Change allowance enabled:** When enabled, this will allow the configuration of a number of Change time allowances to link to Orders on the planning board. The planning resources will have capacity blocked for the specified change time.

**Automatic:** When enabled a pre-defined change time allowance will be attached automatically to an Order when it is loaded onto the planning board. A Change matrix is used to determine which change time to use.

**Using Product Attributes:** When enabled a pre-defined change time allowance, defined on the Product, will be attached to an Order when it is loaded onto the planning board. A Change matrix is used to determine which change time to use.

### Update

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Update*

This page controls manual production updates and how they are applied. Production updates that are imported may be similarly configured in the Import configuration section.

#### Options

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Update › Options*

> **Note:** There are two methods for recording production updates:

- Incremental (default), where the quantity made on the specified date is added to previous total. If the same quantity is accidentally entered twice then this method can double book entries.
- Cumulative, where the total quantity made to date is entered every time. This method allows the same quantity to be entered more than once without double booking as the total quantity is always taken. However this method can be more difficult to understand.

Only planned operations can be set to receive incremental updates, all non-planned operations are entered as cumulative figures for each Order. For the planned Operations there are several cumulative methods which may apply:

**Enter cumulative production updates by Order:** When enabled, production figures should contain the cumulative production progress for each Order.

**Enter cumulative production updates by Group:** When enabled, production figures should contain the cumulative production progress for each Order within each planned Group.

i.e. if an Order is split across two planning Groups then the cumulative figure for each Group must be entered (along with a Group reference). The total Order progress will be the sum of each Groups' cumulative progress.

**Enter cumulative production updates by Row:** When enabled, production figures should contain the cumulative production progress for each Order on each planned row.

For example, if an Order is split across two or more planning rows then the cumulative figure for each row must be entered (along with a row reference). The total Order progress will be the sum of each Rows' cumulative progress.

**Include transport method in production updates:** When enabled FastReact will allow you to select a transport method when updating production on the planned operation. Only valid transport methods for the Group/Row will be selectable.

This will be useful if you need to air ship a small quantity of a large strip there will be no need to split the strip and keep it separate from the main strip.

**Maintain 365 day product history:** With this option enabled FastReact will keep a history of each product showing where it has been previously made, how much was made and the defined efficiency at that time. This information will then become available when taking orders from the Load Lists to help plan products in the most appropriate places.

> **Note:** This will add a small overhead to processing production updates so you might not want to enable this feature unless you do need the information it will provide.

**Allow operations to work in different units:** This option will allow operations to work in different units.

For example, in a typical setup the operations may be in Pieces but the user may require that the Finishing operation be measured in Kgs. The Finishing operation MUST also have this option checked on the Operations dialog.

With this option enabled a new column will appear on the Product Add/Amend dialog. This column will be called Factor.

### Variance reporting

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Variance reporting*

**Number of historical days to report:** Normal reports allow a small historical period to be included as these reports normally look forward in time. However variance reporting, by definition looks backwards. This field will hold how many days of history to include in these reports.

For more details on these options please contact the FastReact support desk.

### Flows

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Flows*

This tab will only be visible if Flow planning option is enabled within your Company's licence.

**Number of historical days to report:** Normal reports allow a small historical period to be included as these reports normally look forward in time. However flow reporting needs to be a combination of historical data and future plans. This field will hold how many days of history to include in these reports.

**User flow name:** Placing a name in this field will create another column in the flow column with that name. This column can then have a flow against it.

#### Options

*Context: Main Menu > Setup > Configure > Production › Configure Production Options › Flows › Options*

**Use Master flow dialog:** This option will switch the view from the standard Flow dialog to the Master Flow Schedule dialog.

**Auto create a flow for new orders using order:** This option will allow FastReact to create a Flow from the Order name without user intervention.
