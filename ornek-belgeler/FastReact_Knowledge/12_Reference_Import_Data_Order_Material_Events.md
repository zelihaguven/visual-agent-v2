# Reference - Importing Data - Order Material Events

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Order Material Events
**Index keywords:** Order Material Events

---

Order material events may be imported from a file called ORDMATEV.txt or ORDMATEV.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **O.NAME** | T30 | The order code. |
| **O.EVENT** | T50 | The event name or event external ID. |
| **O.MAT** | T50 | The material reference, this is the full name of the material or the external ID can be used. The size of this field can be increased. Click here (see: Main Menu > Setup > Configure > General) for more information. |
| O.DATEDONE | Date | The completed date of the material event. |
| O.DATEEXP | Date | The expected date of the material event. |
| O.NOTE | T30 | This will add a note to the Material Event (Child Event) for the Material Event on the Order. |
