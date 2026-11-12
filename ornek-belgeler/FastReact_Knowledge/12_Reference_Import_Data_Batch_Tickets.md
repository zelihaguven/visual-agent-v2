# Reference - Importing Data - Batch Tickets

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Batch Tickets
**Index keywords:** Batch Tickets

---

Material schedules may be imported from a file called BATCHTICKETS.txt or BATCHTICKETS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **TICKET_REF** | T50 | The unique ticket reference. |
| **OPERATIONS_ID** | T15 | The ID of the operation that is being updated. |
| **SCANNED_DATE** | Date | The date that the ticket was scanned. |
| **SCANNED_QTY** | Integer | The quantity that is scanned in on that date. |
| SCANNED_REJECTQUANTITY | Integer | The reject quantity that is scanned in on that date. |
| SF_SCANNED_TIME | Date / Time | Shop Floor: The time the ticket was scanned in |
| SF_MACHINE_ID | T15 | Shop Floor: The Machine ID of the machine that did the ticket. |
| SF_TECHNICIAN_ID | T15 | Shop Floor: The Technician ID of the Technician that did the ticket. |
| SF_OPERATOR_ID | T15 | Shop Floor: The Operator ID of the Operator that did the ticket. |
| SF_QC_ID | t15 | Shop Floor: The quality control ID for the ticket. |
