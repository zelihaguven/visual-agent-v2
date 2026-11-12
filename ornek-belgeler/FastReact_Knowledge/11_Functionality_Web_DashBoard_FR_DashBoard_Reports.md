# Functionality - Web Dashboards & DashBoard Reports

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Web DashBoard & FR DashBoard Reports

---

## The Web DashBoard

The standard FastReact Evolution ProActive DeskTop module has been superseded by the new Web DashBoard. The Web DashBoard allows the User to graphically display data from a database. The Web DashBoard runs in the Web browser and requires FRS setup.

[Screenshot: WebDashBoard]

#### Main Features:

1. Dashboard drop-down items
2. Data Filter
3. Object Options
4. Dashboard Objects
5. Logout button

[Screenshot: WebDashBoard] In order to allow Users to create their own DashBoard element, we have enhanced the FR Reporting module to allow the User to define and run their own Reports for the DashBoard. The reports are saved to a Database table and from there linked to the FR DashBoard. This function is particularly useful for KPIs.

### Data Filters

[Screenshot: WebDate Filter] Within each dashboard object there are usually filters that allow data to be refined beyond the initial view. For example, in an object such as OTDP by Customer, we may wish to focus on a specific customer, factory or date range. This is done by selecting the filter, selecting a filter criteria and selecting the required values. This will then refine the data to those items selected. Multiple filters may be used for a single object.

### Object Options

[Screenshot: WebObject options]

On each dashboard object there are three options. These are:

**1: Export to Excel / PDF / Image:** This option can export the data used in the object (not the chart) to MS Excel for further manipulation. Export the image to a PDF file. Export to an image file.

**2: Maximise object:** This option will maximise the object to full screen.

**3: Refresh:** This option will refresh the object.

**4: Filters:** **T**his option will filter the object.

**5. Clear Filters:** **This option will clear the filters on the object.**

**6. Settings**

 This option allows changes to be made to the appearance of the object and change object/type.

### Dashboard Objects

[Screenshot: WebObject options]

Each dashboard object may have multiple hotspots that will respond to mouse click. The Y-axis key may be linked to an external report or other item accessible by hyperlink. The value of the label will be appended to the link.

Clicking the bar chart may result in a ‘drill down’ further into the data. This will enlarge and further information will become available.

This ‘drill down’ may have further levels of information available, by clicking the new bar chart in the same way.

[Screenshot: WebObject options]

## Dashboard Reports

[Icon: Func DashBoard Reports]

Configuration of these Reports will require the input and help of FRS, as they are security protected. There are also Microsoft configurations that need to do done prior to using this functionality.
