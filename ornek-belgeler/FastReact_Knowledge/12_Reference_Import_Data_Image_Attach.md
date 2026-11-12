# Reference - Importing Data - Image Attach

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Image Attach
**Index keywords:** Image Attach

---

Attached images for Products may be imported. To be more precise, it is not the attached image itself which is imported but the Network path to the location of that image that is imported.

The data may be imported from a file called IMGATTACH.txt or IMGATTACH.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| **IMG.CODE** | T30 | The reference code for the product. |
| **IMG.FILENAME** | T15 | The actual name of the image file. |
| **IMG.NAME** | T255 | What the image that is to be attached will be called. |
| **IMG.FILEPATH** | T255 | The location of the image that is to be attached. |
| IMG.DEFAULT | Boolean | Whither the above image is to be set as the default image or not. Pass a ‘ 1 ’ for Default and a ‘ 0 ’ for Not Default. |
