# Main Menu - Setup - E-Mail - E-Mail

**Source:** FastReact Help (version 4.44) — User manual
**Menu path:** Main Menu > Setup > eMail

---

## Setup E-Mail

*Context: Main Menu > Setup > eMail › Setup E-Mail*

FastReact can send and receive data using e-mail. This functionality is used for Distributed Planning Boards, FR Remote, Collaborative Planning and Reporting. It can also be used as part of Fast React Systems Ltd ongoing programme of product improvement as all system errors can be e-mailed to our support desks every day for analysis.

**Update (button):** This button will update all changes made on this dialog.

### General

*Context: Main Menu > Setup > eMail › Setup E-Mail › General*

Enter configuration settings here that affect how your email system will operate.

#### Outgoing mail

*Context: Main Menu > Setup > eMail › Setup E-Mail › General › Outgoing mail*

**Send mail by:** Emailed data can be sent in a number of different ways.

##### Method

**Integrated:** Use FastReact integrated mail system. This needs to be configured before use.

**Outlook:** Use Microsoft Outlook mail system.

**Mapi:** FastReact uses the Microsoft Mail Application Programming Interface. This requires that e-mail is configured on the workstation and, where more than one e-mail client is defined FastReact will use the one that you have defined as the default. This could be Outlook, Outlook Express or any other MAPI compliant email client.

**Lotus Notes:** For detailed setup instructions and explanation of the use of Lotus Note and the Domino Server please see here.

**Server (SMTP):** Enter the name of the SMTP account that you want to use to send mail. If the Integrated mail system method has been selected for use then this entry is essential, otherwise it should be left blank. The document Email Client Setup explains the setup procedures for each of the email configurations from a client PC perspective.

**Sent from name:** Enter a name that will be used to identify emails sent from FastReact.

This can be anything, for example, the company name or even just 'FastReact'.

> **Note:** Certain virus checkers may reject mail that does not contain this data.

**Return address:** This is not strictly required unless using the FR Remote (RAS), or Remote Update Program (RUP) however, certain virus checkers may reject mail that does not contain this data.

**Split emails:** Checking this option will allow the user to send a report to multiple users. The report will be attached to separate emails, one for each selected recipient.

#### Incoming mail

*Context: Main Menu > Setup > eMail › Setup E-Mail › General › Incoming mail*

**Receive mail by - Method:** ##### Method

**POP3:** FastReact requires a POP3 account to be established. This can either be on the existing email service provider or it could be on the internal mail server.

> **Note:** If using Lotus Notes create a POP3 account for FastReact to use.

**Lotus Notes:** Only check this box if the Lotus Notes option has been selected as Outgoing Mail format. See here for more information.

**Outlook:** Use Microsoft Outlook mail system.

**Pop3 Server:** This is the IP address or name for the POP3 server to which the account name and password belong.

**Lotus Notes Database File:** This is name of the Lotus Notes database file. This field will only be enabled if the Lotus Notes option on the "Receive mail by" method is enabled.

**Account name:** FastReact will need to know the account name from which to collect emails. Normally this would be set up as an account specifically for this purpose.

For example, "FastReact@mycompanyname.com" .

> **Note:** Another account must set up if Distributed planning is to be used.

**Password:** Enter the password relating to the email account name entered in the above field. This is needed in order to collect mail from the above account.

### Remotes

*Context: Main Menu > Setup > eMail › Setup E-Mail › Remotes*

FastReact can send and receive data to subcontractors, remote factories and suppliers. They can also send data back to FastReact to update progress and so on. This is described in the section on Remote Requests.

Sent from name and Return address (above) must set up the for this to work.

#### Automatically send requests

*Context: Main Menu > Setup > eMail › Setup E-Mail › Remotes › Automatically send requests*

FastReact can be configured to send out data packages automatically on a weekly or daily cycle. Each package can be sent daily or weekly.

**Weekly:** Enter the week day on which you want to send the weekly packages

**Daily:** Enter which days of the week you want your daily packages sent.

**Time to send:** Enter the time of day that you want the data packages sent. 00.00 cannot be used as a time.

### Plug out boards

*Context: Main Menu > Setup > eMail › Setup E-Mail › Plug out boards*

**Return plug out boards to (email address):** An email account must be specified which must be reserved for the receipt of returned plug out planning boards only. This is because FastReact will try to process any mail that it finds in this account. If it finds mail that is not correctly formatted it will create an error.

**Minutes between automatic check for plug out responses:** FastReact can be configured to check the email account above on a periodic basis. Any mails that it finds in the account will be processed immediately.

> **Note:** Automatic checking will only be carried out when the 'service' user is logged on.

**Select days of the week on which to check:** You can enable the automatic checking so that it is only carried out on certain days of the week.

**Allow Read only plug out boards to be sent by FTP.:** FastReact can, when enabled, send the plug out boards to an FTP site. This option is a one way transaction.

### Collaboration

*Context: Main Menu > Setup > eMail › Setup E-Mail › Collaboration*

##### Email account to check for package for received packages and handshaking

**Email address:** If Collaboration is enabled, an email account must be specified which must be reserved for the receipt of 'handshaking' data.

**Received mail by:** ##### Method

**Pop3:** Select this option if using Pop3.

**Lotus Notes:** Select this option if using Lotus Notes.

**Server (POP3):** Enter the POP3 address here.

**Lotus Notes Database file:** Enter the Lotus Notes Database file address here. This will only be enabled if the Lotus Notes Received mail by method is enabled.

**Account name:** This is the name of the Email account relating to the Email Address defined above.

**Password:** This is the password for the email account.

### Error logs

*Context: Main Menu > Setup > eMail › Setup E-Mail › Error logs*

**Enter an email address here and FastReact will send its error log files to this destination.:** For example, support@FastReact.co.uk will send all error logs to the Fast React Systems Ltd help desk.

##### Debugging support. Only enable if specifically request by Fast React Support Staff

**Include chronological menu option log:** When selected the error logs that are sent to FastReact will included the menu options that the users has entered during the planning session.

For example,

System: Windows 2000 Professional, Version: 5.0, Build: 893, "Service Pack 4"

MDAC Version: 2.80 Jet Version: 4.00.8618.0 (post SP8)

Processor: Intel, Pentium III, 1060 MHz MMX. Display: 1024x768 pixels, 32 bpps

Memory: Physical 27/238 Mb. Page file 392/577 Mb

User FRS, 20.09.04 - 13:37:43

Logged on to E:\"PROGRAM_NAME"\ACCESS\apparel.MDB

User FRS, 20.09.04 - 14:14:22

Setup - General - Configure

User FRS, 20.09.04 - 14:14:36

Setup - Configure - Plan options

User FRS, 20.09.04 - 14:14:47

Planning - High level board

User FRS, 20.09.04 - 14:29:11

Setup - Configure - Plan options

Additional debugging support

When selected the error logs that are sent to FastReact will included additional information that will be of use to the FastReact technical department.

For example,

Serial number: - none -

Version info: 4.1.408.644 Db: 40821 Rel: 15.09.2004 Expires: 31.01.2005 (133)

Install path: C:\Documents and Settings\Desktop\FR4.exe

System: Windows 2000 Professional, Version: 5.0, Build: 893, "Service Pack 4"

MDAC Version: 2.80 Jet Version: 4.00.8618.0 (post SP8)

Processor: Intel, Pentium III, 1060 MHz MMX. Display: 1024x768 pixels, 32 bpps

Memory: Physical 20/238 Mb. Page file 389/577 Mb

User FRS, 20.09.04 - 14:56:56

HL Plan Sri Lanka, section Despatch, 0 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

HL Plan Morocco, section Despatch, 5 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

HL Plan Australia, section Despatch, 2 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

HL Plan, section Despatch, 86 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

LL Plan Morocco, section Despatch, 0 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

LL Plan Australia, section Despatch, 0 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

LL Plan Sri Lanka, section Despatch, 0 strips, Loaded from database

User FRS, 20.09.04 - 14:56:56

Logged on to E:\"PROGRAM_NAME"\ACCESS\APPAREL.MDB

**Address of your support desk:** Enter here the email address of the FastReact support desk. This is used when emailing the database directly from with FastReact to support.
