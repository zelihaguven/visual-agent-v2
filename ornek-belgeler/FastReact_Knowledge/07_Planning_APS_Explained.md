# Main Menu - Planning - APS

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Planning > APS Explained
**Index keywords:** APS Explained

---

## APS

*Context: Main Menu > Planning > APS Explained › APS*

FastReact has an optional automatic planning module which would be used where the volumes of orders to plan exceed that which can be comfortably planned manually or where the availability of materials and the loading of non planned operation capacity must be strictly respected. As can be seen, the APS function does not optimise as such, but it can be configured to automatically perform a series of user defined execution plans and give a score to each, allowing you to select the best result. This gives a good compromise between finding the 'best' solution and ease of use/execution time.

APS requires a High Level planning board, although systems with Low Level planning can also use APS to allocate orders into groups for detailed low level planning if required. Any planning decisions that are made at low level, such as Build Up Allowances will be respected by APS.

### Introduction

*Context: Main Menu > Planning > APS Explained › APS › Introduction*

There are two decisions to be made when planning an order and these decisions are precisely the same whether planning manually or when planning automatically. They are:

- 'Where do I plan this order?' and;
- 'When do I plan this order?'.

Of course both decisions, written like this seem trivial, but, as always, it gets more complicated when the decision is needed with real orders. Also the two decisions cannot always be made in isolation as there will often be some interaction between them. When planning manually there will be a number of factors that will be required to take in to consider. To APS these factors must be converted into simple rules that a computer can use to derive a plan which the Planner will find acceptable. FastReact uses a simple rule set which the Planner should find intuitive and easy to configure.

Configuration is described below.

### Where to plan

*Context: Main Menu > Planning > APS Explained › APS › Where to plan*

Unless the Planners are very lucky, or perhaps only have a single resource (factory, subcontractor) then there will be a series of rules that must be applied when deciding on where to plan an order. These rules include:-

**Which resource can make the order:** Inevitably certain resources may be able to make a particular product and others may not. It would be no good expecting a suit manufacturer to make underwear and vice versa.

**Can one resource make the product better than the others:** Additionally, the Planners may have a number of resources that can all make a particular product, but not equally well (in terms of efficiency or cost).

**Is there transport from the resource to the customer:** It's no good planning an order into a resource if there is not transport available to take the finished goods from the resource and deliver it to the customer or to the customer's distribution centre.

**Are there any special factors that must be considered:** The normal rules will allow a specific product to be made in a number of different resources, however, the Planners may want to refine the list of suitable resources according to additional rules.

For example they may have already had costings done and want to force the order to be planned in the resource which gave the best costing.

These rules could be applicable at the product and/or order levels.

**Which resource will give me the best on time delivery performance:** The Planners may prefer to plan an order in a resource which has a lower efficiency than another suitable resource, but would give a better delivery date to the customer.

**Force a specific resource:** The Planners may want to force APS to use a single specific resource on an order by order basis.

### Loading policy

*Context: Main Menu > Planning > APS Explained › APS › Loading policy*

FastReact allows the Planners to select different loading policies which influence it's decision on where to plan orders. For example:

**Equalise load:** APS will attempt to load all resources equally so that they are filled to similar dates. This might be a good option if the Planners are loading their own factories.

**Maximise efficiency:** APS will always use the resource which is most efficient for each product. This could result in one resource being filled well into the future and another one hardly loaded. This might be the best option if the Planners subcontract.

### When to plan

*Context: Main Menu > Planning > APS Explained › APS › When to plan*

There are two options when determining when to plan an order. These are to plan 'As Soon As Possible' (ASAP) or 'Just In Time' (JIT) and the decision on which to use will be determined by circumstances.

#### Planning ASAP

*Context: Main Menu > Planning > APS Explained › APS › When to plan › Planning ASAP*

FastReact will fill resources and maintain full production until the plan run out of orders (assuming adequate materials supply). This will almost inevitably result in higher than necessary inventory as orders may be made earlier than the customer delivery date. A company with its own manufacturing to fill would probably prefer this method as the cost of having idle plant may be prohibitive.

#### Planning JIT

*Context: Main Menu > Planning > APS Explained › APS › When to plan › Planning JIT*

FastReact will attempt to make each order so that it available as close to the customer's delivery date as possible. This will tend to leave holes in the utilisation of capacity but would result in lower inventory as finished goods will be dispatched to the customer as soon as each order is completed. It is, however, possible that there is just not enough capacity to make all orders before their delivery date. In this case FastReact will have no alternative than to plan them late but it will position them as early as possible to minimise the degree of lateness.

The Planner can mix these two options on an order by order basis so that some are planned ASAP and others planned JIT.

#### Planning extent

*Context: Main Menu > Planning > APS Explained › APS › When to plan › Planning extent*

APS has a fixed planning extent of 1024 days. This gives the plan a planning period of around 3 years.

### Interaction

*Context: Main Menu > Planning > APS Explained › APS › Interaction*

When automatically planning, FastReact will work out the best resources for orders an then attempt to plan the order according to the ASAP/JIT rules. If it cannot plan the order satisfactorily (delivery late) in the 'best' resource then it will try all other possibilities and finally plan the order in the resource which gave the best delivery performance.

### Order prioritisation

*Context: Main Menu > Planning > APS Explained › APS › Order prioritisation*

FastReact has a single pass algorithm to achieve a really fast planning solution. This means that orders are placed into the plan one at a time and once placed they will not be moved again. Clearly for this to give an acceptable result orders must be planned so that the ones with the highest priority are given the first opportunity to grab capacity and materials, followed by orders in descending priority sequence. Under normal circumstances priority can be simply calculated from the order delivery date. However FastReact gives you a number of different propitiation algorithms to choose from which would allow you to favour one customer over another, or plan high added value orders first and so on.

Additionally, the Planners may want to lock specific orders in place so that the planning algorithm will not move them, instead fitting other orders around the locked ones. In this case the locked orders will always have highest priority and be placed first on the existing resource and on the current date. Any order which has been manually planned will be so locked. However, these can be (optionally) moved by APS if it finds that there is insufficient materials cover at the planned position.

> **Note:** Any orders planned on a Low Level planning board are unconditionally locked and will not be re-planned under any circumstances. Likewise any order that have started in production will not be re-planned (unless there is inadequate materials cover) to ensure continuity of production. This can be overridden on an order by order basis for to allow orders that have been 'put on hold' to be re-planned.

### Primary capacity constraints

*Context: Main Menu > Planning > APS Explained › APS › Primary capacity constraints*

This is the capacity of the planned operations as defined when setting up the Plan groups. Any adjustment to working hours that you have made on the high level planning board will also be taken into account. You can also define additional rules that allow capacity to be flexed over a fixed time scale allowing future periods to be scaled up or down by a fixed percentage each week.

The primary capacity can be considered finite (hard) or infinite (soft). If you select finite primary capacity then planned resources will not be overloaded and orders will be planned to this finite limitation even if this results in late deliveries. You can select infinite capacity and orders will be allowed to unreservedly overload the available capacity. If planning JIT this would allow the true picture of capacity requirements over time to be visualised, however if planning ASAP all orders would be planned right from the start of the plan. The combination of ASAP and soft primary constraint is of doubtful value.

### Secondary constraints

*Context: Main Menu > Planning > APS Explained › APS › Secondary constraints*

In addition to the Primary capacity constraint APS can also take into account the capacity available on secondary (non planned) operations so that these are never overloaded. This might mean that primary capacity resources may well be under loaded if secondary operations hit their limits first. APS will attempt to fill any such primary resource loading shortfall with other orders that make less (or no) demand on the secondary operations. In this way it will attempt to maximise the utilisation of the primary resources.

Secondary constraints can be flagged as finite (hard) or infinite (soft). If infinite, APS will still calculate loading for these operations so that you can perhaps review a recruitment, subcontract or overtime policy. Additionally, individual operations, may be flagged as Infinite or Finite when defining Operation parameters allowing only critical operations to be considered in the planning process and others ignored. All operations can be flagged in a specified Group to be marked Infinite.

### Materials constraints

*Context: Main Menu > Planning > APS Explained › APS › Materials constraints*

FastReact can take account of materials as a finite or infinite resource. If flagged as infinite FastReact will ignore materials availability when calculating the plan. You can then run materials requirements reports within FastReact to get a picture of the materials that would be required to satisfy the plan. You may not be able to get these materials of course.

If materials are flagged as finite, FastReact will not plan any order that cannot be fully satisfied by materials that are either in stock or will be delivered from the supplier by the time they are needed. Materials for orders that are not fully satisfied will be retained by that order to ensure it can be produced ahead of lower priority orders or, optionally, they can be returned to the available 'pool' to be used by other orders.

Materials can have individual lead times, the time the supplier would need between taking an order from you to delivering the materials to your factory. Orders that cannot be satisfied with current materials availability will be planned to start after the longest lead time for required materials, making the assumption that materials could be made available by then.

### Plan options

*Context: Main Menu > Planning > APS Explained › APS › Plan options*

There are a number of additional options as described in the configuration section.

### What can be planned and where

*Context: Main Menu > Planning > APS Explained › APS › What can be planned and where*

#### Efficiency profiles

*Context: Main Menu > Planning > APS Explained › APS › What can be planned and where › Efficiency profiles*

FastReact makes use of Efficiency Profiles to identify where a specific product type can be made or sourced. As all individual products are grouped into product types, configuration is easier to set-up and maintain, than if profiles were set up for each product. If you do need to be able to configure APS to work, not by product types, but at the product level, you can do this, however you would set up efficiency profiles so that any product type could be made on any resource.

#### Product properties

*Context: Main Menu > Planning > APS Explained › APS › What can be planned and where › Product properties*

Each planned group (resource) can be given properties. This is just a text string of characters that describe, in some logical way, the capabilities of the group. Similarly, each product can be given a property text value to match against the group property. Where there is a mismatch the group can be eliminated as a possible resource. Property matching makes use of wild cards to allow a flexible solution. Product properties can contain multiple entries to allow matching to a range of different resources. This option will refine the selection made by the efficiency profile and may eliminate some groups.

> **Note:** If a plan group has a valid property, but the product property is missing then that group will be considered invalid for that product.

#### Order properties

*Context: Main Menu > Planning > APS Explained › APS › What can be planned and where › Order properties*

In the same way, each order can have a property text string to match to the group property. This option will override the selection made by the product properties and may force a specific range of groups.

#### Order plan in group

*Context: Main Menu > Planning > APS Explained › APS › What can be planned and where › Order plan in group*

If you select a specific group for an order then only this group will be used.

#### Transport

*Context: Main Menu > Planning > APS Explained › APS › What can be planned and where › Transport*

Make sure that there is a transport route defined between the planning groups and your customer's location. If you never make any goods for a specific customer in a specific group then you do not need transport defined.

### When can orders be planned

*Context: Main Menu > Planning > APS Explained › APS › When can orders be planned*

#### Capacity

*Context: Main Menu > Planning > APS Explained › APS › When can orders be planned › Capacity*

Make sure you have set-up proper capacity values for your groups. This includes calendars and holidays. You should have done this already during FastReact's initial configuration.

### Materials

*Context: Main Menu > Planning > APS Explained › APS › Materials*

Make sure you have entered stock, expected deliveries and lead times for all materials that you want to be included in the APS calculations.

### Why was an order not planned?

*Context: Main Menu > Planning > APS Explained › APS › Why was an order not planned?*

Not all orders can be planned. In such cases APS will return orders to the load list for manual intervention. However, the occurrences of unplanned orders should be few and APS will generate a log explaining exactly why each order failed. The most likely causes are:

#### No suitable group

*Context: Main Menu > Planning > APS Explained › APS › Why was an order not planned? › No suitable group*

This may happen when suitable groups have been selected for the product but they have then all been eliminated by additional selection criteria.

For example, there may not be any transport to the customer from any of the possible groups, or you may have forced the selection of a group that cannot make the product.

All possible reasons will appear in the log to allow easy investigation and correction

#### Reached the end of the plan

*Context: Main Menu > Planning > APS Explained › APS › Why was an order not planned? › Reached the end of the plan*

You just have too many orders to plan. Remember APS has a planning extent of nearly 3 years so the chances of seeing this error should be quite rare, unless all of your orders are directed to a single resource. Remember also that lack of materials should not normally cause a problem as materials are considered to be freely available after their lead time has expired.
