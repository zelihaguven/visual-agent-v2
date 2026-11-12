# Functionality - Now and Next Work Content Effective Date

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Now and Next Work Content Effective Date
**Index keywords:** Next Work Content Effective Date, Now

---

## "Next route" licence option

### How it works.

The idea behind this piece of functionality is to allow the Planner to define when a Route will change on the Product and have the planned strip redraw itself based upon where it is planned in conjunction to the defined Effective Date.

When licenced, (FRL), the Work content by operation and route part of the Products Add & Amend dialog will display a "+" icon against the Route(s):

[Screenshot: Work Content Plus]

Click on either one of these [Screenshot] plus signs will display the following dialog:

> **Note:** This example is using the "Pieces" work content Route.

[Screenshot: Work Content Plus Now Next]

On this dialog the user can set the date from when the new Route values will take place, (Next effective from); the current Work Content, (Now); and the following work Content, (Next). It is these Next work content values that will be picked up on the planning board and affect the strip.

So, from 10/04/2011 the strip should automatically resize as per the "Next" column. Now on the planning board the planner will see:

[Screenshot: Work Content Plus Planning Board]

Notice that when the strip moves past the 10/04/2011 that is automatically resizes based upon the new Work Content rules.

### Caveats for this functionality:

The start of the strip must equal or start after the assigned "Next effective date" for the "Next" work content to be applied.

The strip will take the "Now" work content if a production update has been done before the new effective from date, unless the strip is replanned AND the original end date of the strip did not o over the effective date.
