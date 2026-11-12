# Functionality - Plug Outs

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Plug Outs

---

## Plug Outs.

### Plug Out Types.

- Update (and View) Only Plug Out.
- View Only Plug Out.
- Full Plug Out.

##### Additional Options.

If the Plug Out boards are set to either Update (and View) only or View Only, then these option will be unavailable. However, for Full Plug Outs, additional options can be set. Please see here (see: Main Menu > Setup > Planning > Planning Boards) for a list of these options.

#### Update (and View) Only Plug Out.

> **Note:** This configuration is not compatible with Complex or Advanced routing.

There are two setting for this.

##### Global (licence file set as Update).

If the Plug Outs are licenced as Update Only then the Remote will only every return planned and non planned updates to the Host. Any other changes made at the Remote site will not be returned. With this setting ALL Plug Outs returned from the Remote will only ever contain Updates.

##### Distribution settings (Update only for remote user).

The Global licence file may say Full Distribution but each board can be individually set to Update Only. This allows a multiple Plug Out distribution system to configure a board as Update Only whilst the other boards may be Full.

#### View Only Plug Out.

> **Note:** This configuration is not compatible with Complex or Advanced routing.

There are two setting for this.

##### Global (licence file set as View Only).

If the Plug Outs are licenced as View Only then the Host can only Send boards. With this setting ALL Plug Outs sent from the Host will not allow the Remote to be sent back to the Host. The Remote site will not have the option to return the boards back to the Host.

##### Distribution settings (View only for remote user).

The Global licence file may say Full Distribution but each board can be individually set to View Only. This allows a multiple Plug Out distribution system to configure a board as View Only whilst the other boards may be Full. Again the Remote site which receives this View Only board will not be able to return the board.

#### Full Plug Out.

There are two setting for this.

##### Global (licence file set as Full).

If the Plug Outs are licenced as Full then the Host can Send/Receive all altered data. With this setting ALL Plug Outs sent from the Host will contain an exact copy of the board in the Host. The Remote site can change and update all options related to the Planning board sent out by the Host.

##### Distribution settings (View only for remote user).

The Global licence file may say Full Distribution but each board can be individually set to View or Update Only. There are also other options which the Host can optionally allow the Remote site to alter.
