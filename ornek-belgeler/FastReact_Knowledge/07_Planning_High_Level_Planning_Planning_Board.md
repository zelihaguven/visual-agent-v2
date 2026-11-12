# Main Menu - Planning - High Level Planning - Planning Board

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > High Level Planning > Planning Board
**Index keywords:** Planning Board

---

## High Level Planning Board

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board*

The planning board occupies the top half of the High level plan and shows individual orders represented by coloured strips running across the screen. The left hand side of the screen shows information about each order whilst the body of the planning board shows where each order is planned.

### High level board display types

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types*

There are two ways in which the High Level Planning Board can be visualised.

- Traditional High Level view.
- Drop Down High Level view.

A description of each of these views can be found by following the links above.

#### Date scale description

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Date scale description*

[Screenshot: Date scale]

The date scale along the top of the planning board can be altered using the [Screenshot: Left Right Move] buttons. This will either decrease or increase the date scale. The dates above the days of the weeks on the date scale are the week end dates as defined during setup.

#### Information scale

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Information scale*

The information scale is divided into a number of different elements.

**Section button (optional):** This button shows the colour of the section in which the order is planned. You can click on this button to filter the planning board to show just those parts of your orders that are planned in this section. This is a quick way of selecting a single section in a cascaded system. If your planning system is configured as a single section then this button will not be displayed.

**Text data:** This data will vary according to the display rotation that you have chosen. See below. If the text is underlined then it is an indication that the order has notes attached. These can be viewed by selecting the Notes option on the right click strip menu.

- [Icon: strip colours] These three buttons represent: Strip colour Product colour Customer colour

**Strip colour indicator (button):** This button mirrors the colour that would be displayed on the strip itself. This is useful if the strip has been scrolled off the left or right of the screen as any problems that might be highlighted by the strip colour can still be seen in this indicator.

**Customer button:** This button shows the colour associated with the customer for each order. You can also filter the planning board to show just those orders for the selected customer by clicking on this button.

**Product button:** This button shows the colour associated with the product for each order. You can also filter the planning board to show just those orders for the selected product by clicking on this button..

**Status indicator button:** This button shows various strip status as below:

- [Icon: Lock] This icon indicates that the strip is planned on a group that has been locked by another planner. These strips cannot be moved.
- [Icon: LL planned] This icon indicates that the strip is planned on a low level planning board. Clicking on this icon will force FastReact to display which planning board has control of the strip. These strips cannot be moved.
- [Icon: Manual schedule] This icon indicates that there is a manual schedule attached to the strip.
- [Icon: HL planned] This icon indicates that the strips is in the load list of a low level planning board. If you hover the mouse over this button FastReact will tell you which planning board has control of the strip.
- [Icon] This icon indicates that production has been started on this strip.
- [Icon: APS lock] This icon indicates that the strip has been manually locked so that it cannot be moved by APS. This will only be shown if APS is enabled within your licence terms.

**Display rotation (button):** The High level planning board can show a number of different views of your plan as selected by the display rotation control on the tool bar.

- [Icon: display rotation] Display rotation.

See below for a breakdown of each of the rotations:

- [Icon: Rotation Orders] Orders rotation.

The information scale shows the order reference. The strip colours show the relationship of the strip to the order delivery date and the critical path.

- [Icon: Rotation Order Colours] Order colours/ Product display rotation.

The information scale shows the product reference. The strip colours show the relationship of the strip to the order delivery date and the critical path.

- [Icon: Rotation Products] Products rotation.

The information scale shows the product reference. The strip colour is derived from the product type.

- [Icon: Rotation Product colours] Product colour rotation.

The information scale shows the product colour. The strip colour is derived from the product colour field on the Product Add Amend dialog.

- [Icon: Rotation Product type] Product type rotation.

The information scale shows the product type reference. The strip colour is derived from the product type.

- [Icon: Rotation Customer] Customers rotation.

The information scale shows the customer reference. The strip colour is derived from the customer.

- [Icon: Rotation Delivery] Delivery rotation.

The information scale shows the order reference. The strip colour is derived from the delivery period (week or month).

- [Icon: Rotation Colour] Colour rotation.

The information scale shows the order reference. The strip colour is that which you have assigned to that order type.

- [Icon: Rotation Materials] Materials rotation.

The information scale shows the order reference. The strip colour is derived from the material status.

- [Icon: Rotation Materials F] Material supply rotation.

The information scale shows the order reference. The strip colour is derived from the Normal MRP calculation.

- [Icon: Rotation User Defined] UDF rotation.

The information scale shows the selected user defined field value. The strip colours show the relationship of the strip to the order delivery date and the critical path.

- [Icon: Rotation Event] Event rotation.

The information scale shows the event status. The strip colour is derived from the critical path.

- [Icon: Rotation supply demand] Supply v Demand rotation.

The information scale shows the MRP calculation. The strip colour is derived from the MRP calculation.

#### Planning board strips

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Planning board strips*

Each order is represented by a coloured strip running across the main body of the High level planning board. The horizontal position of the strips shows you, by reference to the date scale, when the order is due to start and finish. You can also put the mouse on the strip to see its date in the upper left hand corner of the board. The length of the strip represents the time to make the order. The strip colour gives you a visual indication of the status of the strip. See below.

#### Types of display

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Types of display*

FastReact offers two different ways to view planning board strips according to the type of business you operate. These are:

#### Manufacturing display (default)

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Manufacturing display (default)*

This display gives a great deal of information about the various phases of production from preparation right through to final delivery to the customer. Each phase is represented by a different part of the strip.

Preparation

This phase, from the start of the first non planned operation through to the start of the planned operation, is represented by a green line to the left of the main strip body. As an example this could show the time allowed for operations such as cutting and embroidery ahead of sewing which would be the planned operation.

Feed on to first production

This represents the time delay from feeding work into the main planned operation to that same work coming out again. In a production line situation this would be the work in progress on the line expressed as days. It is visually shown by a grey line between the Preparation and the start of the main body of the strip.

Strip body

This represents the production time of the planned operation. This part of the strip is coloured to show the status of the order. See below.

Post planned operations

This represents the time required to complete production though any operations that occur after the planned operation. This is represented by a grey dotted line.

Waiting for transport

If your post production transport does not leave every day then there will probably be a delay until the next transport is available. This period is shown as a red line.

Transport time

The time of transport to the next stage (next planned operation), Distribution centre or customer, is represented as a purple line.

Time at the Distribution centre

The time for work that needs to be carried out at the Distribution centre is represented by a pale purple line. If you deliver directly to the customer then this, and the phase below, will be omitted.

Time from Distribution centre to the customer

The time for transport from your Distribution centre to your customer will be shown as a light green line. If you deliver directly to the customer this phase will be omitted.

> **Note:** This phase makes the assumption that transport leaves the Distribution centre every day.

#### Sourcing display (optional)

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Sourcing display (optional)*

This style of strip display gives only that detail which would be of value to a company who subcontract to suppliers. In such circumstances there is no need to know details of the individual phases of production. Similarly details of transport may be superfluous. This style has only two phases.

Production phase

This phase extends from the start of the preparation phase and extends right though to the goods leaving the supplier on return transport. This block uses the normal strip colours described below.

Transport phase

This phase extends from the start of transport to the goods finally reaching the customer. This phase is represented by a purple line.

#### Pre-production phase

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Pre-production phase*

The progress of critical path events can be displayed attached to the left of each strip. This is shown as a pale yellow coloured block. Where the left hand end of this block is before 'Today' then there is a danger that pre-production delays may cause a late start to production, whether this is in-house or at a supplier.

#### Strip colours

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Strip colours*

The High level and Low level planning board strips share the same colour coding. Click here to see the colour coding.

#### Planning window

*Context: Main Menu > Planning > High Level Planning > Planning Board › High Level Planning Board › High level board display types › Planning window*

All orders must be planned within a window which is bounded by the start of the plan (usually Today's date) on the left and the delivery date for the order on the right.

If the display of this window is enabled then the left hand side of the planning board will be shaded (dark grey) to indicate the first available capacity. Any orders which have critical path or production requirements that cross this line must be considered at risk of starting later than planned.

The right hand side of the window shows the delivery date for individual orders and is shown in pale grey. Any orders that are planned so that the production or transport extends beyond the edge of the window will be at risk of late delivery.
