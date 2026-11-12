# Reference - Importing Data - Customer Profiles

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Customer Profiles
**Index keywords:** Customer Profiles

---

Customer Profile details may be imported from a file called CUSTPROF.txt or CUSTPROF.csv

The following fields may be imported. Essential fields are shown in bold, other fields may be omitted.

| Field Name | Type | Description |
|---|---|---|
| **CP.NAME** | T30 | The unique Customer Profile name. |
| CP.NEWNAME | T30 | This is the new profile name if the Profile is being renamed, (optional). |
| CP.DELETE | Integer | This field will delete the referenced Profile, (optional). <br> 1 = Delete <br> 0 = Do not delete |
| CP.CUST | T15 | The for this customer associated with this Profile, (optional). |
| CP.ENABLED | Integer | This field will whither the Customer is enabled in the Profile, (optional). <br> 1 = Enabled <br> 0 = Not enabled |
