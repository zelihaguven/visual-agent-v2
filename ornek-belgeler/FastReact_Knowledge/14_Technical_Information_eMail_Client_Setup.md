# Technical Information - eMail Client Setup

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > eMail Client Setup

---

## eMail Setup

#### Domino/Lotus Notes Server Configuration.

The problem is that the Domino/Lotus Notes server is configured to prevent people from outside the domain using it to send external email.

i.e. someone outside of www.mydomain.com

There is a possible fix for this which the Administrator of Lotus Notes will have to do as follows:

In the Domino Administrator go to:

server >

 configurations >

 (your server) >

 Router/SMTP >

 Restrictions & Controls >

 SMTP Inbound Controls >

There you should find an option:

'Allow messages only from the following external internet hosts to be sent to external internet domains'

This should contain an appropriate entry for your system. Probably something like:

"[192.168.0.\*]; [192.168.1.\*]" (without the quotes). The I.P. addresses will depend on how your server is configured - The server Administrator should know.

This setting will allow internal programs to send SMTP messages. Outside users can't get to these IP ranges since they should not be routed over the Internet & the firewall blocks them anyway.

After changing the setting you may need to Stop and restart the SMTP task.

> **Error: - SMTP rejected for policy reasons:**

> **Note:** If you get this error when sending mail from FastReact the reason may be related to the following:-

You have to check your configuration document (Router/restrictions and controls/SMTP inbound and SMTP outbound). Check which domains can send and receive mail through the server or sub net. Also there is a setting in the .ini file which indicates if relaying is allowed.

### Lotus Notes Configuration

> **Note:** It is strongly recommended that when setting up your email client and or server that accounts are created solely for the use of the FastReact system. This account will be used with Remote packages and Plug Out boards. Both of these options MUST have there own account as, particularly in the case of the Remote packages, FastReact will not be able to access the returned packages if there are non-distributed planning package emails within the designated inbox.

[Screenshot: Email Client Warning]

Using the local instance of Lotus Notes, browse to the nnotes.dll file. This will normally be located at c:\program files\lotus\notes.

Once located go to the environment variable tab in the computer system and edit the PATH

##### Start

From the START menu select CONTROL PANEL.

[Screenshot: Email Start]

##### Control Panel

From the CONTROL PANEL select SYSTEM then ADVANCED then ENVIRONMENT VARIABLES.

##### [Screenshot: Email Control Panel]

##### Environment Variables

From the resultant dialog, see below, select ENVIRONMENT VARIABLES and highlight the path that has to be appended with the Lotus Notes dll. Then click EDIT.

[Screenshot: Email environment]

Add the path to nnotes.dll using ";" to distinguish between the different variables.

On the "Variable Value" …..Files\Microsoft SQL Server\80\Tools\BINN should be appended with the line ;c:\program files\lotus\notes. This is the location path of the nnotes.dll located at the beginning of this section. Click OK twice.

The …..Files\Microsoft SQL Server\80\Tools\BINN is just a running list of referenced locations within the hard drive(s).

Re-start FastReact to allow the application to pick up the new environment variable that has just been created. The PC may require a re-boot.

#### Outlook Configuration.

Follow the instructions on the Outlook wizard when setting up a FastReact account on the client machine. Entering the required information where prompted. Normally account name, passwords and server name and location will be provided by the IT Administrator (The wizard will only appear if no other email account is configured on that machine).

If the FastReact account Inbox is being added to an existing email client follow these instructions.

Click on The Tools menu from within the Outlook email client.

##### Select E-mail Accounts

[Screenshot: Email outlook express new email]

The next dialog that appears is the account set up wizard.

[Screenshot: Email outlook new email]

Here select "View or change existing eMail accounts"

Click Next

[Screenshot: Email outlook new email]

Click on "Change...." and the dialog below appears.

Do NOT alter any of the setting on this dialog. Just click on the "More Settings" button.

The next step is to OK the dialog and let the wizard create the mail box in the client Outlook:-

[Screenshot: Email outlook express new email]

Enter a name for your additional email inbox.

[Screenshot: Email outlook new email]

The new inbox will now be visible from the users Outlook program.

[Screenshot]
