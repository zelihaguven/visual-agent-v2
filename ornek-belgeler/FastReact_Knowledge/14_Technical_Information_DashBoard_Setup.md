# Technical Information - DashBoard Setup

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > DashBoard Setup
**Index keywords:** DashBoard Setup

---

The following setup instructions should only be attempted with the approval of FRS and you Network Administrator.

## Installing And Configuring IIS 7 On Windows 7

To add the IIS functionality to the operating system go to:

[Icon: IIS]

This is also accessible by going to Start --> Run and entering ‘Appwiz.cpl’.

[Icon: IIS] Normally the default settings will be sufficient. To ensure the settings are correct, drill down to Application Development Features (shown) and ensure .NET Extensibility and ASP.NET are enabled. Check that Static Content is enabled under the Common HTTP Features and to improve performance you may also wish to enable Static Content Compression under Performance Features.

For most FastReact web products, the .NET 3.5 and .NET 4.0 frameworks are required, and if not installed should be installed in the order 3.5 then 4.0.

To verify that IIS is installed correctly in Windows, go to Start then Run and enter ‘inetmgr’

[Icon: IIS] Ensure the ASP.NET section is visible, as highlighted above.

> **Note:** If in any doubt during this process, please contact your network administrator.

## Installing And Configuring IIS On Server 2008

Within Server Manager, check the ‘Roles Summary’ and verify that IIS is not currently installed.

[Icon: IIS]

It is possible that the Web Server (IIS) Role is installed but incorrectly configured, or is missing the required features. This will be covered later in this document.

To add the Web Server (IIS) role, scroll to the top of the Server Manager and click ‘Add Roles’.

Click ‘Next’ on the information screen and check the ‘Web Server (IIS)’ check box.

If the ‘Add Features Required for Web Server (IIS)’ dialogue pops up, click ‘Add Required Features’

Click ‘Next’ to get to the ‘Introduction to Web Server (IIS)’ screen.

Click ‘Next’ to get to the ‘Select Role Services’ screen.

[Icon: IIS]

Ensure the ‘ASP.NET’ check box is checked. If the ‘Add Role Services and Features Required For ASP.NET’ dialogue box pops up, click ‘Add Required Role Services’.

Ensure ‘Basic Authentication’ is checked under the ‘Security’ section.

Click ‘Next’.

Verify the installation selections and click ‘Install’.

Once installation completes, select ‘Close’.

Verify that the Web Server (IIS) role is available within the Roles Summary in Server Manager.

[Icon: IIS]

If in any doubt during this process, please contact your network administrator.
