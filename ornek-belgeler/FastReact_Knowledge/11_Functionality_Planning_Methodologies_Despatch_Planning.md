# Functionality - Planning Methodologies - Despatch Planning

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Planning Methodologies > Despatch Planning
**Index keywords:** Despatch Planning

---

## Despatch Planning

[Screenshot: Despatch Planning] ### Theory

When moving strips in a group, that has a despatch group, the strips in that despatch group will have their strip schedule set to match the 'available at next section' schedule for the moved strip. At this point the available and despatch schedules will match and FastReact will report no overlap problems between the strips in these sections. Any replanning of the source section will automatically replan the despatch section. This automatic planning is calculated by delivery and not for the whole order.

### Planning

Despatch planning is only ever done at High Level and never at Low Level, even though the source strips are planned at Low Level.

When planning on the source section, for example, the Sewing section, FastReact will automatically plan the despatch section once the source strip has been planned. At this stage the available and despatch schedules will match and the 'overlap' warning will be cleared.

FastReact will, however monitor the positions of the despatch strips when source strips are replanned and will warn if the despatch strip will miss the customers delivery date. This means that the planner will be able to see a potential late delivery on a Low Level board even though the problem is on a High Level despatch plan which is not visible.

Multiple source strips (split strips) will only have one despatch strip associated with them.

The automatically created despatch schedule will be retained on the strip between sessions. The despatch strip and the source strip(s) form a bond or link which when unbroken will allow the automatic replanning of the despatch strip with respect to the source strip. This automatic link can be broken in a number of ways:

- Splitting the despatch strip;
- Manually entering a schedule and;
- Locking of the strip.

Despatch schedules are recalculated as part of the normal 'refresh' process within FastReact. This ensures that they have the correct data.

### Overriding the despatch plan

The schedule on a despatch strip is calculated from the 'Available at next stage' schedule from the strips in the preceding section. Any transport delays and elapsed time for despatch strips will be taken into account when calculating the relationship between these strips and the final delivery dates. However, when manually entering despatch shipments the user will need to enter dates and quantities for when the despatches are actually expected to happen. In this case FastReact will need to ignore the transport delays but still add in the elapsed time. Strips that are locked or have a manually entered schedule and as despatch strips will obey these new rules.
