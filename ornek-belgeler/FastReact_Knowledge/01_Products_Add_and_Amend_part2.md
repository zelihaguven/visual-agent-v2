# Main Menu - Products - Add and Amend (part 2)

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Products > Add and Amend
**Part:** 2 of 3 — sections: Define tab, General, Financial, Materials, Changes, Optimise, Property Match, Events

---

### Define tab

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab*

There is a lot of information that planner may want to enter about the products. Some information is, however, essential and is presented on the first page (General) of the Define tab. Optional information is available on subsequent tabs.

**Product reference:** Enter a unique code for the product up to 30 characters long, or use the Incremental search list to help to find existing products

> **Note:** We would advise a consistent naming convention for products as this will make future operation much easier. We strongly recommend that spaces are not used as part of the product name and, as such FastReact will strip from the beginning and end of the product name any spaces found.

**Document attach (button):** - [Icon: Document1 Attach] Attach documents to this product.

Multiple documents can be attached to each product. These documents will be held in a central repository from which FastReact can access them. Click here (see: Functionality > Document Attach) for more details.

**Image attach (button):** - [Icon: Image Attach] Attach an image to this product.

Multiple images can be attached to each product. These images will be held in a central repository from which FastReact can access them. Only the default image will be visible on the Planning Board. Click here (see: Functionality > Image Attach) for more details.

**Material Item:** This check box will mark the Product as a Material Product.

**Created:** This will be the system generated date on which the Product was created on FastReact.

**Insert/Update (button):** This button inserts or updates the product into the database.

**Delete (button):** This button deletes the product from the database.

**Notes (button):** This button brings up the Notes dialog.

#### General

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › General*

**Description:** This is an optional entry of up to 50 characters long. It can be used to describe the type of product such as "100% cotton pleated trouser". If a description is entered here then it will be used as the default description for orders that are subsequently created for this product.

**Product Type:** Select a product type from the list. Attaching a product type to a product will allow you to define working efficiencies by Group for your product.

For example: Product type "mens shirts" in factory 1 line 2 work at 95% but in factory 2 line 3 the same product type runs at 80%.

For a more detailed look at product types please click here (see: Main Menu > Setup > General > Product Types).

> **Note:** If this product is inherited from another product then the Product type will be taken from that product and changes made here will be ignored.

**Property:** Data cannot be entered here, however this field will mirror the data entered in the Property tab below.

> **Note:** The "Mirror this value on general tab" must be enabled on the Property Matching tab for this to be visible.

**Sizes required:** **Size set:** This drop down list will hold a the name(s) of pre-defined size sets. These sets are setup on the Sizes dialog on the Setup – General menu.

**Sizes required:** This list will present you with all of the sizes you have defined. Tick those that you want to select for this product.

> **Note:** Only the sizes selected here will be available for orders that are created using this product.

**Default Critical Path:** A default Critical Path can be applied to a Product which will automatically be picked up by the Order when the Product is attached to an Order.

##### APS Values

**Base Date:** This date, when set to anything other than 01/01/2000, will be used in the APS calculations as the start date from which Strips may be placed on the Low Level Boards. This field will only be visible if APS enabled.

**Priority:** This field will only be visible if APS enabled. This allows the altering of the planning priority of this specific order.

**Stock:** This field will only be visible if the Plan Line calculation (Net Requirement Planning) option enabled.

##### Pre Production

**Customer:** Optionally, customers can be selected for the product.

**Timetable:** Selecting of a Development timetable allows the control of the development events for this product. This field will not be visible unless Development Event planning is enabled.

**Launch date:** This field is used in conjunction with the development timetable above. This date will be used when calculating event target dates using the offsets within the selected timetable.

**Inherit launch date:** If this check box is ticked then it signifies that the Launch Date has been inherited from another product. This is only visible when the product has inherited the launch date from the Parent product.

**Colour (button):** The colour of the product can optionally be defined to represent the actual colour of a dye-lot or the fabric / thread colour. The planning board display can be rotated to view this colour to ensure a logical colour progression on a production line or dye vessel.

**Archived (button):** This check box indicated whither or not the Product has been Archived.

##### Work content by operation and route

This is a list of operations and routes that was created earlier. Enter the work content into the operations and routes that have been defined. Work content must be entered against the planned operation to create a valid product. FastReact will prevent the saving of a product with zero work content. The work content is used by FastReact to calculate the amount of capacity required to produce a required quantity of the product.

Work content can be inherited from another product. If it is, data cannot be entered here.

**Operation:** This is a valid list of the operations for this product.

**Units:** These values are user defined on the Operations dialog.

**Factor:** This column will only be visible if the option to "Allow operations to work in different units". This is configured on to Production dialog and the Operations dialog against the particular operation. The work content for the operations which have been assigned as "different units" will appear as blue on the Products Add/Amend dialog.

**Descriptors:** This licence option allows for many operations of the same or similar names to be easily identified via their Descriptors.

**Min Qty:** These fields, against the operation, allow the user to define the minimum quantity that can be made in that operation for the defined Product.

> **Note:** This is a client specific option.

**Inc Qty:** These fields, against the operation, allow the user to define the increase quantity that can be applied to that operation for the defined Product.

> **Note:** This is a client specific option.

**Routes:** (for Parallel Route functionality click here (see: Functionality > Parallel Routings) or for Next Route functionality click here (see: Functionality > Now and Next Work Content Effective Date))

Depending upon what has previously been set up, there can be one or more columns into which work content can be entered.

For example, Pieces, SMVs and Kgs.

- [Icon: Work Content Plus] "Next Route" is licenced on the FRL.

When "Next Route" is licenced, (FRL), the Work content by operation and route part of the Products Add & Amend dialog will display a "+" icon against the Route(s). This allows the planner to override the work content on a Product from a certain date and have this reflected on the Planning Board

- [Icon: Left Right Move] Move between work content values on the Operations table.

##### Routing

- [Icon: Product Routing] Create the Routing for the product..

This button will enable the user to define the Routing for the selected Product. This manually created Routing will define the operation route though which the associated Order will follow. More information can be found here (see: Functionality > Parallel Routings).

#### Financial

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Financial*

FastReact can produce financial reports based around selling price, material costs, labour costs and other costs. This tab enables you to enter this information. However FastReact is not a financial package, and has not been designed to replace existing financial packages. Financial information can be used for simple calculations and reporting purposes.

> **Note:** Security settings can be configured so that sensitive data can be withheld from certain users, for further details please see the documentation relating to Security settings.

##### Enter financial values for this product

**Selling price:** Enter here the selling price per unit for this product.

**Material costs:** Enter here the cost per unit of all materials.

**Labour cost:** Enter here the cost per unit of labour.

**Other direct costs:** Enter here other costs per unit associated with the product, this could include processes outside your factory such as Embroidery, and Dyeing or a nominal unit value for fixed overheads.

**User defined fields:** FastReact will allow the user to define other financial fields to suit their own particular circumstances. These fields can be given a value on a product by product basis. These can then be used for reporting purposes. These user defined fields must have already been created.

#### Materials

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Materials*

FastReact offers the user the ability to calculate material requirements against planned production. The information within this tab is used to define the materials required and the requirement of each material per item of product.

Material details were defined earlier.

##### Inherit from

If you have inherited materials from another product you will not be able to enter data here.

The entry table has the following columns.

##### Materials table

**Category (optional):** This entry is optional.

Each material requirement is picked from a list of materials shown below the table. Under most circumstances just the material Specification (below) would be required to fully define the requirement. However, there may be times when this is just not enough.

A good example would be where a weaver might require the same yarn in his warp and his weft. The user could enter the yarn once and also the combined requirement for both warp and weft as a single usage value. This would be fine in the calculation of total requirements but it would be inadequate in determining the timing of the requirement. This is because weft yarn will be consumed over the production period of the order whilst the warp yarn will all be required before the order can start in weaving. To overcome this problem the user can create two materials, one called 'WARP' and the other called 'WEFT' and set the Phased flag on each accordingly.

When FastReact performs materials calculations it will use the settings for any materials in the Category column to override the settings in the Specification column.

**Disable:** When enabled, this option will allow the user to select and deselect materials which will be used on the Order BoM. This field is also importable.

**Specification:** Set the material specification in this column.

**Material usage / size range:** The next columns allow the user to enter a usage value, that is the quantity of material per item of this product.

If the size option is enabled and there are selected sizes for this product then the user must enter values for material usage per size. This allows the user to define different materials per size as well as different usage per size.

**Fill across (button):** - [Icon: Product Copy Usage] Fill values across.

This button will, when clicked, automatically fill in the Usage/Sizes fields with the value entered in the first highlighted field on the particular row.

**Move (button):** - [Icon: Left Right Move] Move between sizes values on the Material sizes table.

**Search for materials:** If there are a large number of materials then FastReact can help find the required one by means of a search list. Enter the first few characters of the material required and FastReact will filter the list automatically.

##### Materials list

To add materials to the specification list, drag them with the mouse into the appropriate column. To remove a material set its usage to zero.

**Display material descriptions (if available):** This option will replace the Material Names in the search list and on the BoM with the associated Material Description.

**Do not mix materials from different suppliers:** This option is not available unless the user has materials calculations within the terms of their licence.

Materials may be purchased from a number of different suppliers. When calculating materials availability against requirements, FastReact will normally add together the stock and delivery from all suppliers. If, for any reason, the user would prefer that each product be satisfied from a single supplier then enable this option.

**Do not mix alternative materials.:** FastReact will allow the user to specify up to 9 alternatives for each material required on the product. This information can only be imported, not manually entered. When FastReact performs materials calculations of availability against requirements it would normally try to satisfy a requirement from a single material. Failing this it will top up availability from alternatives, if any. Enable this option if you want to ensure that a product is only made from a single material of the alternatives.

> **Note:** If you have 'Do not mix materials from different suppliers' switched on this option is automatically switched on.

**MRP uplift percent (imported).:** This is the imported value that the MRP calculation will automatically add on when FastReact is doing its MRP calculations. This can only be imported in to FastReact.

> **Note:** This is a client specific option.

#### Changes

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Changes*

The default change times can be overridden by entering a new value in this table. The Change time (minutes) is used to calculate an accurate load against capacity for each Operation.

For example: A machine may require 40 minutes to change between two different Products, this time is then not available for production and must be subtracted from the available capacity to give an accurate picture.

> **Note:** This tab will not be visible unless you have enabled the Change Allowance option.

**Operation:** This is a list of all the valid operations for the particular product.

**Change:** This is the amount of time that the operation requires before the next operation can start.

#### Optimise

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Optimise*

This tab will only be accessible if, during set up you have switched on optimise loading. This is done via the Main menu - Setup - Configure - Planning menu option and the new licensing system.

This option is normally used on systems that are planning machines rather than operators. The user can set-up certain constraints for each machine and then, for each product, parameters can be defined to assess the suitability of that product type on that machine.

For example, A 153cm width loom can only produce products with a width below 153cm and for reasons of efficiency may be restricted to Products with a minimum width of 130cm. If the optimise value for a product is 125cm, that is outside the acceptable range, then FastReact can do one of two things, it can prevent you from loading this product on this machine, or it can warn you of an issue by turning the text background light blue.

**Factor:** This is a list of the factors that were set-up earlier.

**Value:** Enter the optimise value (integer) for each factor.

#### Property Match

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Property Match*

FastReact can help the planners to match your individual Products to particular production lines, machines or factories. It does this by comparing properties for each row (machine) with codes that have been entered against each Product. Properties are text strings of up top 60 characters long and can be subdivided into multiple entries by pressing Enter (thereby inserting a CR LF pair in the string).

Matching of the product property to the resource property can be a simple comparison of the text or can be extended by the use of wild card matching.

Row properties are set during Row configuration whilst Group properties are set during Group configuration.

> **Note:** This value can be inherited from another product.

##### Inherit property

When this option is enabled the product has inherited its Property value.

**Mirror this value on the general tab:** With this option enabled, the Property values for the product will appear on the Property List on the General tab of the product.

#### Events

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Events*

This tab contains a table of event names as defined in the timetable attached to this product. The table has the following columns:-

**Event:** This column shows the event names as defined in the development timetable that is attached to the product.

**Target date:** This is the calculated event target date based from the Launch date on the General tab.

**Offset / Duration:** This column shows the default offset and/or the default duration in the development timetable for that event.

**Fast track:** If required the user can override the default offsets by entering new values. This may be used when a product needs to be 'fast tracked' through the development process. Enter the new offset into this field.

**Skipped:** Check this field if that event does not need to be included for this particular product.

**Ignore on PP planning board:** Checking this option will hide the events on the Development Timetable associated with the Product on the Critical Path planning board.

#### User Values

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › User Values*

The user may want to add some other information relating to a product that does not have a pre-defined field. FastReact will allow additional fields for this purpose. These fields can then be given a value on a Product by Product basis and can be used for reporting purposes. User defined fields must first be defined during initial configuration.

**Default capacity factor:** This is the default capacity factor that is defined for the associated Product.

**WiP Overlap quantity:** The WiP overlap quantity will be used for calculating the minimum quantity that must exist as WiP between planned stages.

##### Plan line values.

As well as planning purchase orders at a supplier or works orders at a factory, FastReact can calculate what purchase orders (PO’s) and / or works orders (WO’s) are required in the first place. This module is normally applicable to branded or make to stock businesses.

Firstly FastReact calculates the net demand (usually on a week by week basis) based on a combination of forecast and sales orders and a company specific demand policy.

Secondly FastReact calculates the net requirements by location based on existing supply (stock and existing PO’s / WO’s) plus the ordering policy (safety stock, minimum and incremental order quantities).

FastReact then automatically creates suggested planning orders (Suggested PO’s or suggested WO’s) that meet the net requirements.

**Safety Stock (weeks):** When calculating the Net Requirement FastReact will aim to create supply (suggested) orders such that the stock will equal the specified number of weeks demand.

**Minimum order quantity:** This is the minimum order quantity for which MPS can create suggested orders.

**Incremental order quantity:** This is the incremental quantity for which MPS can create suggested order above the minimum order quantity.

**Demand calculation:** The demand policy is usually highly specific to each FastReact client and is programmed specifically to meet the needs of that business. Pre-configured options include:

- MFC – Maximum of Forecast or Customer orders
- FO – Forecast orders only
- CO – Customer orders only

**Do not include stock quantity in calculation:** When enabled, the opening stock will not be included when calculating the Net Requirement.

#### Batch Quantity

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Batch Quantity*

The user may want to set a Product Batch Quantity if using Batches. This can be done here:

**Product Batch Quantity:** Used in conjunction with Batch Tickets, this field allows the User to set a default Batch qty for the Product.

#### Size stock

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Size stock*

The user may want to record Stock and Minimum stock of a Product by Size. This can be done on this tab.

As well as planning purchase orders at a supplier or works orders at a factory, FastReact can calculate what purchase orders (PO’s) and / or works orders (WO’s) are required in the first place. This module is normally a

**Size:** The size available to the Product.

**Stock:** The current Size Stock of the Product.

**Minimum:** The minimum Size Stock for the Product.

#### Colours

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Colours*

When the Colour Management facility is enabled, FastReact users can enter Colours in the Colour Setup dialog. If the FastReact system has the Purchase Orders module licenced, then the user will be presented with the option, Limit colour selection to product, under the Options tab.

##### Available colours.

This is a list of all the colours available in FastReact. These colours are defined in the Colour Setup dialog.

**Filter colours containing:** this is a quick filtering field. The user will start to type in the desired colour and FastReact will automatically filter all the colours which contain the typed letters.

##### Valid colours for this product.

This is a list of the colours which are available for this product. To assign a colour to a product just drag it from the Available list to the Valid list. If the Valid list is empty them the product can have all colours from the Available list available to it.

**Add colour (button):** This button will add a new colour to the Colour Setup dialog. This is a Supervisor only option from the Products dialog.

#### Suppliers

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Suppliers*

##### The following suppliers are authorised to handle this product.

This is a list of all the suppliers available in FastReact. Checking or ticking the supplier in this dialog will mean that only these suppliers can be used with this product. This option is linked to the Purchase Order option, Limit supplier selection to product.

#### Attribute

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Attribute*

The Attribute field name will automatically rename itself to the name as it is defined in the Attribute setup. These attributes allow FastReact to automatically set change over times based upon changing attributes on planned strips.

**Attribute 1:** The first defined attribute.

**Attribute 2:** The second defined attribute.

**Attribute 3:** The third defined attribute.

**Attribute 4:** The fourth defined attribute.

#### Constraints

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Constraints*

This Licence option will be a list of pre-defined Constraints which can then be applied to each Product Size.

#### Hyperlinks

*Context: Main Menu > Products > Add and Amend › Add & Amend › Define tab › Hyperlinks*

This option has been developed to allow communication to an external system to monitor and communicate the status of CP events. This is a weblink storage facility to enable users to directly link, click and open a web browser which would direct straight to the status of that style, order and event.

Additionally, the weblink facility can also be used to connect to other web base storage system such as drop box if the client’s have style imagery stored online.

This functionality allows web links to be stored against a Product. The link behaves like a hyperlink and opens the location, in a browser, when it is clicked on.

The option is enabled via the FRS logon and is found under SETUP - SYSTEM - Product Options.
