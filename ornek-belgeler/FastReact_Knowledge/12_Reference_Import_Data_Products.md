# Reference - Importing Data - Products

**Source:** FastReact Help (version 4.44) — Reference
**Menu path:** Reference > Import Data > Products

---

Products may be imported from a file called PRODUCTS.txt or PRODUCTS.csv.

The following fields may be imported. Essential fields are shown in bold.

| Field Name | Type | Description |
|---|---|---|
| (On General Tab) | | |
| **P.CODE** | T30 | The unique product code. This field cannot be left blank. |
| **P^WC: n** | Float | Work content by operation. The product must have valid planned work content else it will be rejected. <br> ' n ' = the external ID for the operation. <br> Where work content for multiple routes needs to be imported add 1000 to the external id for the second route, 2000 for the third route and so on. <br> But see P.TYPE |
| **P.TYPE** | T15 | Product type - field will be validated against list of FastReact product types and any that are found to be invalid will be set to the first product type in the list. <br> Work content (P^WC) can be inferred from P.TYPE in this case P^WC can be omitted. |
| P.OLDCODE | T30 | If the code passed in this field is a valid FastReact product then that product will be renamed to the code passed in the field above. |
| P.DESCRIP | T50 | Product description. The size of this field can be increased . |
| P.TIME | T15 | Product development timetable name. This field will be validated against the list held in FastReact. |
| P.LAUNCHDATE | Date | Launch date for development events.. |
| P.CUST | T15 | A default customer for a product, this can be overridden at order level. |
| P.SIZESET | T15 | This is the size set name. |
| P.SIZESELECTION | Boolean | Used in conjunction with P.SIZESET, this field will automatically enabled the sizes defined on the P.SIZESET for the product. <br> 0 = Do not enable the sizes on the size set. <br> 1 = Enable the sizes on the size set. <br> Note: <br> Sizes can be defined on the Product but a "1" will over rule the defined sizes with the Sizeset. |
| P^SIZENAME: n | T25 | Multiple sizes to be available on this product where ‘ n ’ is a sequential number from 1 upwards. New sizes can be created on import. |
| P.APS_BASE_DATE | Date | The APS base date. |
| P.MAT_ITEM | Boolean | This is the check box to indicate that the Product is a Material Item. |
| P.ARCHIVED | Integer | Product is archived: <br> 0 = Not archived. <br> 1 = Archived. |
| (On Financial Tab) | | |
| P.SPRICE | Float | Product selling price. |
| P.MATCOST | Float | Product material cost. |
| P.LABCOST | Float | Product labour cost. |
| P.OTHCOST | Float | Product other (material) cost. |
| P.Fv name | T15 | Product Financial user defined fields. The size of this field can be increased . <br> Note:- <br> Name = The name given to the UDF’s. |
| P.REJPC | Float | Product reject percent. |
| (On Material Tab) | | |
| P^MC: n | T50 | Material category where ' n ' is a sequential number ( 1 to many ) to define the material category on a product. |
| P^MN: n | T50 | Material name/specification where ' n ' is a sequential number ( 1 to many ) to define multiple materials on a product. |

*(table continued)*

| Field Name | Type | Description |
|---|---|---|
| P^MU: n | Float | Material usage per order unit of the product where ' n' is a sequential number ( 1 to many ) to define multiple materials on a product. |
| (On Changes Tab) | | |
| P^CM: n | Integer | This is the change minutes. |
| P^OV: n | Integer | Optimise values for the product where ' n ' is the External reference for the optimise factor. |
| (On Property Match Tab) | | |
| P.PROPS | T60 | Product property for resource matching. |
| (On User Values Tab) | | |
| P.Ud name | T15 | Product user defined field value where ' name ' is the name given to the User defined field. The size of this field can be increased . |
| P.CAPACITY_FACTOR | Integer | When enabled, this option will import the Capacity Factor on the Product. |
| P.STOCK | Integer | Used for Plan Line calculations. |
| P.MIN_STOCK | Integer | The minimum size stock for the Product. |
| P.PRIORITY | Integer | Used for APS. |
| P.MINSTOCKWEEKS | Integer | This field is only used when FastReact is configured to calculate demand. |
| P.MINORDERQTY | Integer | This field is only used when FastReact is configured to calculate demand. |
| P.INCORDERQTY | Integer | This field is only used when FastReact is configured to calculate demand. |
| P.IGNORESTOCK | Boolean | This field is only used when FastReact is configured to calculate demand. <br> 1 = ignore stock. <br> 0 = include stock. |
| P.DEMANDCALC | T15 | This field is only used when FastReact is configured to calculate demand. <br> MFC <br> FO <br> CO |
| P.ADDMINSTOCKQTY | Boolean | If checked, the minimum stock will be added to the stock policy rather than the stock policy being made up to the minimum. |
| (On Attributes Tab) | | |
| P.ATTRIB_1 | T30 | The Change allowances using Product Attributes. |
| P.ATTRIB_2 | T30 | The Change allowances using Product Attributes. |
| P.ATTRIB_3 | T30 | The Change allowances using Product Attributes. |
| P.ATTRIB_4 | T30 | The Change allowances using Product Attributes. |
| (Other import fields) | | |
| P.INHFROM | T30 | The base code of the product from which you are inheriting information. <br> This product must exist in FastReact or appear earlier in the import file. |

*(table continued)*

| Field Name | Type | Description |
|---|---|---|
| P.INHWC | Boolean | Inherit work content: <br> 0 = Do not inherit. <br> 1 = Inherit. |
| P.INHMATS | Boolean | Inherit materials: <br> 0 = Do not inherit. <br> 1 = Inherit. |
| P.INHPROPS | Boolean | Inherit properties: <br> 0 = Do not inherit. <br> 1 = Inherit. |
| P.INHLAUNCH | Boolean | This is the check box to indicate that the Product has inherited its Launch date. |
| P^CF: n | Integer | Operation conversion factor. ' n ' = Operation External ID. <br> Note: <br> This import field is only applicable when using P^WC: n |
| P^SCF: n | Integer | Section conversion factor. This is only used when the batching function is enabled. <br> FastReact uses this value to calculate the number of batches in an order. <br> ' n ' = External section ID. |
| P^PMD: n | Integer | Allows the standing time by Product to be imported, where ' n ' = operations external reference. |
| P.ORDERTIMEFENCE | Integer | When APS in Licenced, FastReact has the ability to input an timefence by product to be considered by APS. |
| P.ROUTE_PROFILE | | This is the Product Routing name that will be applied to the Product upon import. <br> Note: <br> This import field is only applicable when Parallel Routing is licenced. The field will be ignored if Parallel Routing is not licenced, the value in the field is blank or the Product is being updated. <br> Importing this field will automatically overwrite the existing Product Routing |

FastReact can allocate alternative materials for a product.

For example, if material 1 is not available then it will check for material 2 etc.

Up to 9 alternative materials can be specified for any one material. Alternative materials must be imported in order of preference using a single place decimal for the sequential number 'n'. Only one material usage may be defined for alternative materials

For example

| O^MN:1.1 | O^MN:1.2 | O^MN:1.3 | O^MN:2.1 | O^MN:2.2 | O^MN:3 |
|---|---|---|---|---|---|
| Blue 120 | Blue-300 | Blue-320 | Carded Cotton | Combed Cotton | 11X20 Box |

In the above example 'Blue-300' is the first alternative for the item 'Blue 120' and 'Blue 320' is the second alternative. 'Combed cotton' may be used as an alternative for 'Carded Cotton'. There is no alternative for the item '11x20 Box'.
