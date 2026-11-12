# Functionality - Planning Methodologies - Distributed Planning

**Source:** FastReact Help (version 4.44) — Functionality / concepts
**Menu path:** Functionality > Planning Methodologies > Distributed Planning
**Index keywords:** Distributed Planning

---

## Distributed Planning

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning*

### Introduction

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Introduction*

FastReact may be configured for High Level and Low Level planning boards where the High Level is used to allocate orders to suppliers and the Low Level boards are used to plan those suppliers in detail. So High Level is only concerned with broad issues of which supplier may best fulfil the order and whether it will have sufficient capacity to deliver as required. Low Level will be concerned with which production line, or lines, in the factory would be best suited to the order, whether a learning curve is required, what efficiency overrides may be necessary and so on. This cannot be normally achieved from a centralised planning perspective as detailed local knowledge is essential.

Under normal circumstances the High Level and Low Level plans interact in real time on a Local Area Network, implemented either as hard cabling between sites or though other live connections such as satellite links or high speed data links implemented by an external provider. There will be situations where the necessary data links cannot be reliably implemented. In these circumstances the normal approach would fail with either very poor response times, periods of down time or worse still with corrupted data. It was to overcome these problems that we have developed Distributed planning.

### Overview

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Overview*

Distributed Planning Boards provide a mechanism where Low Level plans may be extracted from the main (host) system and operated as a totally independent system. These can then be subsequently reincorporated into the host plan. The extracted systems can be distributed from the host and returned from the remote site using normal email thereby overcoming the problems of slow or intermittent communications links. The extraction and return process can be driven manually or can be totally automated and can be set to operate on a weekly basis or more often to suit your own requirements.

### Operation

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Operation*

Before use there are a number of issues to be considered all of which revolve around the timing of the extraction and incorporation process. This can be infrequent if plans change slowly or faster for rapidly changing circumstances.

#### Extraction timing (host)

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Operation › Extraction timing (host)*

The extraction process where Low Level plans are detached and sent to the remote suppliers can be controlled in three different ways.

1. The extraction can be performed manually by selecting a menu option
2. The extraction process may be performed automatically on a timer set for a particular time of day and specific days of the week. These settings may be configured independently for each Low Level planning board
3. The extraction process may be performed at the specific request of the remote system. This provides for a good degree of automation and integration between host and remotes.

It is not recommend the use of methods 2 and 3 together as confusion could easily occur.

#### Incorporation timing (host)

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Operation › Incorporation timing (host)*

The incorporation of remote data may also be handled in different ways

1. The process may be performed manually by selecting a menu option
2. The process may be handled on a timer. In this way the host plan will query the email account to see if there are any remote replies waiting. If there are it will incorporate any changes automatically. At this point FastReact would also return an updated plan to the remote, if that remote had requested a new plan (See 3 above)

If a remote has returned more than one plan to the host before the host has had an opportunity to process these then the returned mails will be processed in date/time sequence

#### Return timing (remote)

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Operation › Return timing (remote)*

The return of remote plans to the host may be handled in different ways

1. The process may be performed manually by selecting a menu option
2. The process may be performed at a specific time of day and on specific days of the week. The time should be chosen carefully so that plans are not being changed at the time the plan is sent back. Whilst this will not cause an error it could mean that the returned plan was out of date as it would reflect the last plan that was saved by the planner. The returned plan may also contain a request for a new plan and this may be set to different days of the week to the return days. A request must go with a return however all returns do not necessarily trigger a request. In this way you could elect to have remotes return an undated plan at the close or every day, but only request a new plan twice per week. This would keep the host up to date whilst minimising the work at the remote end.

> **Note:** If the above timing settings are made by the host and cannot be altered at the remote end. Thus the host is always in control of timing. The only override option available to the remote is to manually return a plan. This is provided so that any returns that may have been sent prematurely, or have been lost or corrupted in transfer, may be resent sent.

#### Receive timing (remote)

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Operation › Receive timing (remote)*

The plans that are sent from the host to the remote sites will appear in the In Box of the email account for the remote site. This will then need to be extracted and the data package copied to the correct location. This can only be done when FastReact is not in use at the remote location. To make this task easier we have provided an extraction program (FRPOEXT.EXE) which will automatically back up the current data, extract and decrypt the data package and copy this to the desired location. There are no timed options for this as there is a real danger of overwriting the remote plan at an inconvenient time.

When this program is installed on the computer used to receive emails it can be linked with the distributed package (.FRZ) by selecting the 'Open with' when offered by Windows Enter 'FastReact Distributed Package' as the file description.

### Technical

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Technical*

#### Database requirements

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Technical › Database requirements*

Distributed Planning Board implementation requires that the host system be based on Microsoft SQL Server as the main database. We use specific Microsoft SQL extensions that are implemented in this database to facilitate rapid and reliable data extraction and incorporation.

The data that is extracted and sent to remote sites is in the form of a Microsoft Access database. The package that is sent by email is compressed to ease the email traffic and is encrypted for security.

#### Email accounts

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Technical › Email accounts*

You must provide an email account that the host will check for returned plans. It will assume that any mail found in this account is formatted as it expects and will not be happy if other mails get mixed in with legitimate responses.

#### Registry entries

*Context: Functionality > Planning Methodologies > Distributed Planning › Distributed Planning › Technical › Registry entries*

The following registry entries will be required. Either FastReact or Windows will manage these; there is no need to manually edit the Registry unless there are specific changes that need to be made, this is, however unlikely. In any event DO NOT make changes to the Registry unless you really know what you are doing.

**Database location:** This is held in 'HK_CURRENT_USER\Software\FastReact\Distributed' with a key of 'Extract To' The Update button on the Extraction program will manage this entry for you.

**File association:** This links the data package which is emailed to the remote ('.FRZ') with the extraction program (FRPOEXT.EXE)

There are a number of entries in the registry to handle this association.

HK_CLASSES_ROUTE contains '.FRZ' which in turn contains a default value of 'FRZ_auto_file'.

Also in this folder is an entry 'FRZ_auto_file' which contains the following path and contents 'shell\command\open' = 'path\FRPOEXE.EXE %1' where path is the location of the FRPOEXE.EXE program on your computer.

The default data for this entry is 'FastReact Distributed Package'.

HK_LOCAL_MACHINE\SOFTWARE\Classes also contains the above entries.

WARNING

The Host database MUST NOT be restored to whilst a distributed plan is live. If you need to restore the host database then a new distributed plan MUST be created and the previous one abandoned. Unpredictable results will be obtained if this procedure is not followed.

Updating at the Host site MUST NOT be done whilst the Plug Out is at the plug out site. Any updates you make will severely compromise your data.
