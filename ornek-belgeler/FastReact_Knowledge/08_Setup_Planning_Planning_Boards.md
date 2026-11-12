# Main Menu - Setup - Planning - Planning Boards

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Planning > Planning Boards
**Index keywords:** Distribution, Planning Board

---

## Planning Boards

*Context: Main Menu > Setup > Planning > Planning Boards › Planning Boards*

To be able to use FastReact the user must create at least one Planning Board. Planning Boards are part of the fundamental structure of the FastReact planning system. Planning Boards can be geographical locations including several owned or subcontract resources, different factories or even different departments of the same factory within the business. Each Planning Board can be independently planned at the same time as another Planning Board whilst reporting can amalgamate data from all Planning Boards. Typically one Planning Board is required for each planner. The definition of a Planning Board then becomes 'an area of planning responsibility.'

FastReact is licensed per Planning Board and therefore the Planning Boards will normally have been set during initial installation. The licensing software within FastReact will prevent unauthorised Planning Boards from being created but additional Planning Boards can be purchased and added at any stage to grow the FastReact planning system in line with the business.

### Define

*Context: Main Menu > Setup > Planning > Planning Boards › Planning Boards › Define*

**Planning board name:** Enter the name of a new planning board or select one from the list. Planning board names can be up to 15 characters long.

**Insert / Update (button):** This button will insert a new Planning Board or update an existing Planning Board.

**Delete (button):** This button will delete the currently selected Planning Board.

#### General

*Context: Main Menu > Setup > Planning > Planning Boards › Planning Boards › Define › General*

**Default calendar for groups / rows created for this plan.:** Select the default calendar that the selected Planning Board will use. Any planning groups that are attached to this Planning Board will automatically use this calendar, although this can be amended on a Group by Group basis.

**Default location for transport planning:** Select from the list the default transport Location for this Planning Board. Any Groups that are attached to this Planning Board will be automatically given this Location, although this can be amended on a Group by Group basis.

**Default transport method from this plan:** Select from the list the default transport Method normally used when shipping finished goods back from this Planning Board. Any Groups that are attached to this Planning Board will be automatically use this transport Method although this can be amended on a Group by Group basis.

**Planning board type:** Planning boards can be High Level or Low Level. Low level boards are automatically included in High Level boards, but the planner may not want to have the planning menu cluttered with Low Level boards that are not required viewing. In this case just select 'High level only' here.

**Update operation progress in total not by size:** With this option checked the operation progress will by updated in total rather than by size for the selected planning board regardless of wither the system is set up for updates by size.

##### Licenced sections

A specific number of sections will have been purchased within the licence. These sections can be spread across the planning boards in any way that is required. The list here will show the sections that have created. Each will need to be turned on to make them available for planning. FastReact will check that the licence limit has not been exceeded.

**Total licenced sections:** This is the total amount of licenced sections as defined on the user Licence file.

**Sections unallocated:** This the amount of sections that are still available to be licenced against a planning board.

**Automated Planning System (LL):** When the Automated Planning System (LL) licence option is enabled, the Automated Planning System (LL) option will appear against the licenced section. Each section needs to have the Automated Planning System (LL) applied to it.

**Update (button):** This button will licence the selected sections to the highlighted Planning Boards.

#### Distribution options

*Context: Main Menu > Setup > Planning > Planning Boards › Planning Boards › Define › Distribution options*

This tab will be visible if the Distributed planning option is enabled.

**Send this board with board:** Select another planning board from the list if there is a requirement to send multiple boards to a single location. If the planner selects a board here then all of the options below will be disabled.

**Send this board to:** Select from this list the FastReact user that the board(s) will be sent to. This user must have a valid email address. This option will be disabled if the selected planning board is to be sent with another board, allowing multiple boards to be distributed to a single location

**Time of day to send to remote:** Specify the time of day to send this planning board to the remote location. A time of 00.00 is not valid. The list below will also allow the user to specify which days of the week to send the plan.

> **Note:** This function will only operate for the 'Service' user.

##### Options

**Planning board is view only for remote user:** With this option enabled the selected planning board will be sent as read only board to the remote site. The Plug Out site will be unable to return or update the Plugged Out board.

> **Note:** That by selecting this option, all the other options and update only boards will be deactivated.

**Planning board is update only for remote user:** With this option enabled the selected planning board will be sent as update only board to the remote site. Only updates from the Plug Out site will be returned to the Host.

> **Note:** That by selecting this option, all the other options and view only boards will be deactivated.

**Work content can be changed remotely:** Normally the remote planner cannot change the work content of your products. This is particularly important if products are shared across more than one plan as this could result in one planner making changes that would affect another plan. If the user wants to allow the remote planner to change work content, based on local knowledge, and the products are plan specific then the user can safely check this option.

**Efficiency profiles can be changed remotely:** Normally the remote planner cannot change Efficiency Profiles as they may be shared across several planning boards. Thus changes at one location could, when incorporated back into the host, could cause undesired changes at other locations. Additionally, Efficiency Profiles form a fundamental part of the APS functionality and injudicious changes could have significant and undesirable effects. If Efficiency Profiles are not shared and APS is not being used then the Host planner can allow the remote planner to make changes.

**Operation capacity can be changed remotely:** Normally the remote planner cannot change operation capacity on the loading bar charts, this is usually the job of the host plan planners. However, in some cases the host planners do not manage the operation capacity, as it is the jobs of the remote site planners. With this option enabled any changes made at the remote site to the operation capacity will be reflected back at the host site once a plug out package has been returned.

**Build up allowances can be changed remotely:** Normally the remote planner cannot change the build up allowances, this is usually the job of the host plan planners. However, in some cases the host planners do not manage the build up allowances, as it is the jobs of the remote site planners. With this option enabled any changes made at the remote site to the build up allowances will be reflected back at the host site once a plug out package has been returned.

**Allow materials calculations:** Normally the remote planner cannot run material calculations as it is the role of the host plan, with this option enabled the planner can run material calculations and view the material position for the orders that have been planned or re-planned.

**Bill of Materials can be changed remotely:** Normally the remote planner cannot add or amend any Bill’s of Materials, as this is normally the responsibility of the host planners. However with this option turned on the remote planner can add new material items to products or orders at the remote site. These changes will then be reflected back on the host plan once a plug out package has been returned.

**Maximum rows:** This is the maximum amount of rows that can be sent to the remote user.

**Users:** This is the number of remote users.

##### Return timing

This tab will be visible if the Distributed planning option enabled.

**Time of day to return to host:** Specify the time of day that the revised plan will be returned to the host plan.

> **Note:** This information cannot be changed at the remote location.

**Return to host on:** Specify the day(s) of the week that you want the plan returned to the host.

> **Note:** The plan could be returned every day so that the host plan is kept up to date.

**Request new plan on:** When a plan is returned to the host it can carry with it a request to send a new plan back to the remote planner. Requests can only be made on days that plans are returned.

Using the above mechanism allows for an almost transparent system of linking remote and plans, even if communications are slow and unreliable. Once the first plan has been sent, and this would normally be done manually (from the Tools menu) then new plans will be sent automatically when a revised plan is returned from the remote location. No further intervention is required at the host end.

#### FTP

*Context: Main Menu > Setup > Planning > Planning Boards › Planning Boards › Define › FTP*

This tab will be visible if the FTP option enabled. FTP transfer will allow the user to send large plug outs to an FTP site for pick up from a host or remote site.

Warning:

Please be a ware that this is a one way transfer only. The recipient of the plug out must only be a view only recipient.

##### Send plug out boards to this FTP site

**Server:** Enter the server name or internet address.

**User name:** Enter a valid user name.

**Password:** Enter the required password for the above user name.

**Folder:** Enter the folder name on the FTP site.

### Rename

*Context: Main Menu > Setup > Planning > Planning Boards › Planning Boards › Rename*

Renaming of a Planning Board can take place at any time.

**Select an plan to rename:** This is a list of existing Plans. Select the Plan that requires renaming from the incremental search list.

**Enter a new name:** Enter a new plan name here. FastReact will validate the new plan and only allow a rename to be made if the new plan reference does not already exist.

**Rename (button):** This button will rename the selected plan.
