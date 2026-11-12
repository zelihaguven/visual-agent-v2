# Main Menu - Setup - Activity Scheduler - Activity Scheduler

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > Activity Scheduler
**Index keywords:** Activity Scheduler

---

## Activity Scheduler

### Activity Scheduler

FastReact has an optional Activity scheduler that allows certain functions to be run automatically according to a schedule that you define. This is similar to the automatic functions already in FastReact but is much more flexible. The two approaches are mutually exclusive in that both cannot be active at the same time.

To turn on the Activity scheduler see the Main Menu - Setup - General option on the Defaults page. Once this has been enabled FastReact will pick up the existing schedules and put them into the new schedule. This will be done the first time you re-start FastReact with the Activity Scheduler enabled.

#### Schedule

Select an activity

The following functions can be scheduled

- Import \*
- Run APS \*
- Run Multi stage APS \*
- Send Remotes (RAS) \*
- Exporting \*
- Reports
- Send Collaborative data \*
- Receive Collaborative data \*
- Update KPIs \*
- Email service log \*
- Receive Remote Excel \*
- Seamworks link \*
- Save Variance Report \*

\* If these options are enabled on your system

##### Select a Repeat Type

This drop down field allows the user to select the day of the week that the scheduled activity will take place. The choices are:

| Weekly | The activity will be scheduled to run weekly on the selected day at the set time. |
|---|---|
| Fortnightly | The activity will be scheduled to run fortnightly on the selected day at the set time. |
| Every 4 Weeks | The activity will be scheduled to run every 4 weeks on the selected day at the set time. |
| Per Calendar Month | The activity will be scheduled to run every calendar month on the selected day at the set time. |
| Every X Minutes | Note: <br> This Repeat Type is only available to the Exporting option. |

If the Repeat Type, Every X Minutes is selected then the below Select a Time and Day options will not be available.

> **Note:** This Repeat Type is only available for Exporting.

If the Export option is selected, the Repeat Type, Exery X Minutes will become available. If this is selected the below option will appear:

##### Set frequency (min)

This allows the user to set the frequency of the Export, in minutes.

##### Select a time

This text field allows the user to select a time of day that the scheduled activity will take place. Times are in increments of 10 minutes and either a single or multiple times can be selected.

##### Days of the week

This is a list of days of the weeks which will be used in conjunction with the button below.

**Update schedule for listed day and copy to the selected above (button):** Once the initial day has been set up, selecting days from the Days of the weeks list and clicking this button will copy the initial day setup to those selected days.

> **Note:** Several activities can scheduled to occur on the same day and time. These will be processed sequentially where one activity will run to completion before another activity is allowed to start. However, the sequence that these will be added to the schedule may not be that which is required. To be sure of a specific sequence the user should schedule later activities at a later time of the day. The normal sequence will be as defined above.

##### Additional options

When the activities have been selected for scheduling, additional options may appear for some of these activities.

##### APS configuration

**Execution plan:** This drop down menu box allows the user to select the required APS plan to be scheduled.

##### Remote update package

**Request to send:** This drop down menu box allows the user to select the required Remote destination to which the package will be sent.

##### Export configuration

**Report group:** Select the group to which the required report belong to.

**Report name:** Select the name of the required report.

**Report variant:** Select the variant name of the required report.

**File name:** If the report has a file name this will automatically be entered here.

**Option:** If the report has an option this will automatically be entered here.

##### Report configuration

**Report group:** Select the group to which the required report belong to.

**Report name:** Select the name of the required report.

**Report variant:** Select the variant name of the required report.

**Description:** If the report has a description this will automatically be entered here.

**Option:** If the report has an option this will automatically be entered here.

##### Collaboration package

**Request to send:** This drop down menu box allows the user to select the required Collaboration destination to which the package will be sent.

### Report

This tab allows the user to see a chronological list of activities that have been scheduled. Activities can be deleted by double clicking on them.
