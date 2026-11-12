# Functionality - Plan Line

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Plan Line
**Index keywords:** Plan Line

---

## Plan Line

Occasionally called Net Requirement Planning, Plan Line, or MPS allows FastReact to turn a sales forecast into a requirement to make. This Report is a visual representation of that on a strip by strip basis. This report is accessed via the Low Level right click option, Plan Line.

### MPS Results

**Product:** This is the selected Product that the Report is being run against.

**Product type:** This is the Product Type for the selected Product.

**Stock:** This is the user entered stock qty held on the Product dialog.

**Min order qty:** This is the minimum order quantity for which MPS can create suggested orders, as defined on the Product dialog.

**Firm orders:** This is the number of Orders in the FastReact system for this Product.

**Policy:** This is the

**Increment:** This is the incremental quantity for which MPS can create suggested order above the minimum order quantity, as defined on the Product dialog.

**Demand calc:** The demand policy is usually highly specific to each FastReact client and is programmed specifically to meet the needs of that business. Pre-configured options include:

- MFC – Maximum of Forecast or Customer orders
- FO – Forecast orders only
- CO – Customer orders only

These are defined on the Product dialog.

**Min stock qty:** When calculating the Net Requirement FastReact will aim to create supply (suggested) orders such that the stock will equal the specified number of weeks demand, as defined on the Product dialog.

[Icon: Plan Line]

| Forecast | This is derived from the demand for this Product. |
|---|---|
| **Customer** | This is the amount of confirmed orders already in FR for this Product. |
| **Combined** | This is a setting – do I make forecast order or customer order. In most cases its which is higher of the two. |
| **Policy** | This is the safety stock. Can be week/month/day |
| **Suggested** | Suggest to make rest of stock |
| **Virtual Stock** | If make suggested order, what happens and what do i see <br> In Theory suggested stock should show green |
| **Planned** | What Quantity I have got planned on PB? |
| **Predicted Stock** | What I've got in stock, what order I have and what is going to happen if I carry on with the plan. |
