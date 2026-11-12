# Technical Information - Compacting of Microsoft Access

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > Compacting of Microsoft Access

---

## Compacting of Microsoft Access

Microsoft recommends that you compact Access databases on a regular basis. If you are using an Access database then FastReact will automatically compact it.

### Compacting

If you delete data in an Access database, the database can become fragmented and use disk space inefficiently. Compacting the database makes a copy of the file and rearranges how the file is stored on your disk. This will optimise the performance of the database as well as saving disk space.

Compacting does not delete or purge any of the data from FastReact.

### When compacting is performed

The database will be compacted if:

- The size of the database has grown by either 50% or 5Mb, or
- 14 days have passed,

since the last time it was compacted.

The database will then only be compacted when a user logs in to FastReact and no other users are using the same database. If the database is already in use then the database will not be compacted. If a second user logs in while the first is compacting the database then FastReact will pause and then automatically log the second user in when the compacting is complete. The compacting process should only take a few seconds.

### Disabling

Compacting should only be disabled if it is causing problems in the operation of FastReact.

The option 'Automatically compact Access Database' is located on the 'Defaults' tab in Setup/Configure/General. It can be unchecked to disable compacting.
