# Reference - Importing Data - Customers

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Customers
**Index keywords:** Customer

---

Customers details may be imported from a file called CUSTOMER.txt or CUSTOMER.csv

The following fields may be imported. Essential fields are shown in bold, other fields may be omitted.

| Field Name | Type | Description |
|---|---|---|
| **C.CODE** | T15 | The unique customer code. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| C.DESCRIP | T50 | A brief description for the customer. This could be the full name, address or whatever you want. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| C.LOCATION | T15 | The delivery location for this customer. |
| C.DIST_CENT | T15 | The distribution centre location to be used for this customer. |
| C.DCDAYS | Integer | Offset days for reporting schedules. <br> Note: <br> Can only be used in conjunction with ' Manage suggested orders' . |
| C.LATEOK | Integer | The number of days late after which the planning board will display a ' very late ' status on strips. |
| C.COLOUR | Integer | Strip colour for this customer. |

> **Note:**

> **Notes:** C.COLOUR. This is a 4 byte integer value in the standard Windows RGB() format. There is a Windows API function which will take the Red, Green and Blue intensities (range 0…255) and convert this into a 24 bit colour value.
