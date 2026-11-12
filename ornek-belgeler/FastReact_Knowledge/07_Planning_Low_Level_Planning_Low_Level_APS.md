# Main Menu - Planning - Low Level APS

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > Low Level Planning > Low Level APS

---

## Low Level APS.

Low Level APS is a rule based automated planning method that can plan many orders at a time. This is a licence file option so will need to be enabled in order to use the functionality.

##### How it works

Once licenced, from the Low Level planning board select the APS icon, this will display the setup and options for the Low Level APS functionality:

[Screenshot: LL APS]

Selecting the Setup option will result in the dialog below:

[Screenshot: LL APS]

## Define

On the first use of this functionality, the Low Level APS rule(s) will need to be setup. These rules will define how Fast React deals with each Order, for example where, when and how it is planned.

**Enter APS run name:** Enter the name of the APS run that will be created during this setup.

#### General

**Run description:** This will be the User defined name of the Low Level APS Run that is being configured.

**Use time fence:** This will open when enabled, will, along with the option below force the Low Level APS Run to take in to consideration Time Fencing.

**Time fence days:** This is the number of days that FR will time fence when running the Low Level APS run.

**Ignore progress check:** Enabling this option means that FR will ignore any production that has been done and may replan Order that are already in production.

**Max size:** This option will determine that maximum size a strip can be. This field is measured in ***Minutes*** and not order quantity or strip quantity.

**Max strip count:** This is the maximum split count that an Order can be split during the Low Level APS Run. This is normally used in conjunction with the above option.

**Continue build up:** The option will force FR to apply follow on Build Up Curves to the strips after Low Level APS has replanned the strips.

**Critical path check:** This option will either Ignore, use Critical Events or use All Events on the Critical Path. This means that the Low Level APS will take into consideration the Critical Path when planning or replanning strips.

**Late delivery tolerance:** This will allow the Low Level APS run to plan Orders/strips with in a specified number of days of the Orders delivery date.

#### Order sorting

This will tab will allow the Planner to define how the Low Level APS run handles the Order/Strip sorting.

There are a number of field sorting options:

- Product type code
- Product type UDF
- Product code
- Product UDF
- Customer code
- Customer UDF
- Order code
- Order status
- Order UDF
- Delivery/Required date
- Quantity

#### Row sorting

This will tab will allow the Planner to define how the Low Level APS run handles the Row sorting.

There are a number of field sorting options:

- Product type
- Product type efficiency
- Product
- Product UDF
- Order UDF
- Earliest strip start
- Earliest strip finish

### Excluded rows

This will tab will allow the Planner to define which Rows are to be excluded from the Run.
