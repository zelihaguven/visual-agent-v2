# Main Menu - Setup - Configure - Event Planning

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Configure > Event Planning
**Index keywords:** Event Planning

---

## Event Planning Options

### Configure

#### Production Events

**Production events enabled:** This option turns on Order based critical path planning.

**Allow inheritance:** This option enables the inheritance of events on the order dialog. Only available under licence.

**Show materials within event schedule:** This option enabled will show Order Material requirements that are linked to each event in the Event Framework. These will be visible in the strip Events dialog and in Reporting in the By Event for all Orders loop.

**Material by order only:** This will only show materials on Orders that have a material only.

> **Note:** Allow inheritance and Show materials within event schedule are mutually exclusive.

Show materials by order.

**Default production days:** For FastReact to calculate the Release Date (see Event framework) it needs to know the date on which the relevant order is planned to start. If an order is not planned then it will calculate the Release Date from the earliest delivery on the order, less the number of days that are enter here.

#### Development Events

**Development events enabled:** This option turns on Product based critical path planning.

**Automatically link launch date to planned strips:** Normally in FastReact the planner would have to manually enter the "Launch date" against each product, by using this option FastReact will automatically set the launch date to the earliest planned strip for the product.

**Link to Preparation date:** Normally in FastReact you have to manually enter the "Launch date" against each product, by using this option FastReact will automatically set the launch date to the earliest planned strip for the product.

**Link to Start of strip:** Uses the Production start point as the date for linking launch dates in CP.

**Problem if plan later than Launch date:** When enabled FastReact will colour the strip orange if the strip is planned later than the launch date.

**Problem if plan earlier than Launch date:** When enabled FastReact will colour the strip orange if the strip is planned earlier than the launch date.

**Set Launch date to "Today" for new products:** When enabled FastReact will automatically set the launch date of any new products to the same day as it is created..

**Allow update of event start dates:** Allows the start date column to be viewed and edited in the Event Update Dialog for the critical path.

**Update (button):** Update any changes to the dialog.
