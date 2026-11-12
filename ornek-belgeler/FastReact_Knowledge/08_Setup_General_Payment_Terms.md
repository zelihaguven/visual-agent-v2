# Main Menu - Setup - General - Payment Terms

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > General > Payment Terms
**Index keywords:** Payment Terms

---

## Payment terms

This dialog will hold a list of Payment types. Each payment type must be created individually and will be used in the Cash Flow report to determine when Invoices are due to be paid.

The payment terms define both the quantity and the due date of payments relating to a Purchase Order. Different payment terms exist for different suppliers so multiple Payment Terms can be defined.

**Name:** This is the user defined Payment term name.

**Description:** This is a description of the Payment term.

**Materials:** This check box selects wither or not the payment term is a Material term.

**Update (button):** This button will update or insert a new Payment term.

### Define phased payments

The Payment Terms are broken down into several elements. This breakdown defines the percentage of the total value to be paid, the value itself that is to be paid (e.g. payment to supplier, VAT, Freight, Duty) and the timing or due date of the payment.

**#:** A system defined incremental number.

**%:** This is the percentage of payment of the total value due at the set point below.

**Due at this point:** The point at which the payment becomes is defined through a link to an existing critical path step (via drop down list).

**Offset days:** An offset in days (positive or negative) may be defined relative to the event link point to allow the actual payment due date to be later or earlier than the critical path event due (target) date, as defined above.

**Value:** This is defined through a link to an existing financial field on the Product. Each Value on a Payment Term Breakdown will be linked to a Product financial UDF. The same UDF may be used for several different Breakdown items to allow phased (percentage) payments for the same value to be defined.

**Third Party:** A check box to indicate if the Breakdown is for a third party payment..

**Update (button):** This button will update or insert a new Payment term.
