# Functionality - Planning Methodologies - Variable Planning

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Planning Methodologies > Variable Planning
**Index keywords:** Planning Methodologies, Variable Planning

---

## Variable Planning

The purpose of the variable planning board is to allow the capacity of each strip on the planning board to be varied, this way of planning is used where the planning resource is not fixed but can change dependant upon the style that is being produce on that resource.

### How it Works

On the Low Level planning board, the planning row, which has been designated as 'variable', will have the available capacity for any day calculated exactly the same as for a finite planning row.

When the first order is loaded onto the planning board the strip will take the default value from the row as the number of operators being used on this product. To change the number of operators right click on the strip, select properties and type in the new number of operators in the field labelled 'Factor' in the capacity factor adjustment options.

Alternatively, type in the required quantity per week in the 'quantity per week' field and click the calculate button. FastReact will then work out the number of operators required based upon the typed in figure.

If an order starts with 6 operators and then increases to 9, the strip can be split so the first part of the order takes the 6 operators and the second part takes the 9 operators.

To do this split the strip at the required day or quantity. The first part can then be set to have 6 operators and the second part set to 9 operators. Under normal circumstances when two strips for the same order are placed on top of each other they will combine to form one strip. In the case of variable planning the strips are kept separate by checking the 'keep separate' option on the second strip. This allows the second strip to be moved up to the first strip without combining them.
