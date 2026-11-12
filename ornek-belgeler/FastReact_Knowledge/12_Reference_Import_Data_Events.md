# Reference - Importing Data - Events

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Events
**Index keywords:** Events

---

Event progress for both Production (Orders) and Development (Products) may be imported. Using a separate import file, rather than the event fields within the orders and products import files gives more flexibility and the option to import a wider range of data. This is the recommended option.

The data may be imported from a file called EVENTS.txt or EVENTS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field _ Name | Type | Description |
|---|---|---|
| **E.CODE** | T30 | The reference code for the order or product. |
| **E.TYPE** | T1 | Pass a ' O ' if the code above refers to an order or a ' P ' if it refers to a product. |
| **E.EVENT** | Integer | The external reference of the event as you have defined within FastReact. Use of external references allows the event to be renamed without compromising the import file. |
| E.DONE | Date | The date when the event was completed. |
| E.AD | Date | The achievable date, (Expected Date), for this event. |
| E.SKIP | Boolean | Pass ' 1 ' to skip the event or ' 0 ' to not skip the event. |
| E.OFFSET | Integer | The offset to be used to override the current offset defined in FastReact. |
| E.NOTE | T80 | A brief note to be attached to the event update. |
| E.OVERRIDEEXEC | T30 | This is the name of the user - works for both orders and products. |
| E.TIMEDONE:n | hh:mm | This option is a Client specific import only option. It will allow the importing of the time of the Event completion. <br> Note: <br> It only works when the Licence option Record production completion time is licenced <br> It is only available as an import, it cannot be manually entered. <br> It is only applicable to E.TYPE = O. |
