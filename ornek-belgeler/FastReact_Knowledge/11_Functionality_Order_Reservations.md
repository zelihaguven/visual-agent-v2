# Functionality - Order Reservations

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Order Reservations
**Index keywords:** Order Reservations

---

## Order Reservations

This functionality allows the user to flag an Order as being a Reservation Order and have these Orders displays separately on the High Level Forecast board and the High Level Planning Board. The Reservation status can be imported and/or edited on the Order Add/Amend dialog.

There are two types of Reservation:

- Tentative Reservations
- Confirmed Reservations

Confirmed Reservation will Substitute Tentative Reservations and Confirmed Orders will substitute Confirmed Reservations.

For example,

``` Tentative Reservation > Confirmed Reservation

 >

 Confirmed orders ```

### Configuration

The Order Reservation field can be imported as O.RESERVE_STATUS and reported O.RESERVE_STATUS field.

This status is enabled via the FRS system login under the Setup dialog option it is visible on the Order Add/Amend dialog under the "Reserve" status group.

On the High Level board the order is marked as "<<order>>" for tentative and "<order>" for confirmed reservations

1 = tentative,

2 = confirmed,

anything else = none,

on the ORDERS and ORDUPDAT import files.

To the Order Reservation use the

FRS Option under Order options to turn on Order Dialog option
