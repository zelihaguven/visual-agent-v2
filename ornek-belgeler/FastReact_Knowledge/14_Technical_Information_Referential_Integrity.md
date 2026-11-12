# Technical Information - Referential Integrity

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > Referential Integrity

---

Referential integrity is enforced within FastReact to prevent objects from being deleted that would otherwise render FastReact unstable.

For example, the user cannot delete a product that is used by an order as all orders must have a valid product. If an attempt is made to delete such an object, FastReact will not let the user continue.

There are other circumstances, however, where an object may be in use but the user might want to delete it anyway.

An example might be an operation that has been created and assigned work content against a number of products. The user might subsequently want to remove this operation. In this situation FastReact will allow the deletion but it will warn the user first that the object is in use. These object can be deleted and FastReact will take care of removing traces of the object from within the database. FastReact will remain stable in these cases.

> **Note:** Referential Integrity is not enforced within the FastReact database itself. This gives greater flexibility, but could lead to problems if the database were manipulated directly from outside of FastReact.
