# Technical Information - Licencing

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Technical Information > Licencing

---

FastReact must be licensed before it will operate. There are a number of interlinked components to this licence system and these are described below.

## Licence system components

### Components:

- Key or Dongle
- Licence Server
- Licence Manager
- Licence File (.frl)

## Licence key

This key or 'Dongle' contains a Licence user number, an expiry date and a type. There are three different types of Client Key:

Client, which can be:

- Standard - The standard client key will ONLY work with the client database that it has been programmed to, but it will allow full functionality within that database.
- View Only - This type of key will allow access to the system but the users will be unable to alter either the structure or the data within FastReact.
- Plug Out - This type of key will be operational at remote sites which receive FR Remote or Distributed Planning Boards (Plug Out Boards). It does not have the full functionality of the Standard key but will allow the remote site access to FR Remote packages or Plug Out Boards.

All of these key are pre-programmed by Fast React Systems Ltd. and represent your Licence to run the FastReact software.

FRS accepts no liability to replace lost or stolen keys but damaged keys will be replaced upon receipt of the original to your supplier.

## Licence server

The Licence Server is a small software program which needs to be running somewhere on your network. This could be one of the workstations running FastReact, on the Server, or on any other workstation at all. However, the Licence Key must be physically plugged into the same computer that is running the Licence server.

### Licence Server

The Licence Server comes in two versions.

1. The first is a stand alone executable program and this would normally be started by including a shortcut to the program in the Start-Up folder in the Windows Start menu. This means that the Licence Server will be started automatically whenever you start Windows. This program is called FRLSMGR.EXE. When this is running you will see a small icon on the Windows task bar. This program also doubles as the manager for the service option below.
2. The second option is to run the Licence Server as a Windows service. This will not work in Window 9X versions. The advantage of this approach is that the service can be run on a file server without the need for a user to be logged on as the service will be started by the operating system. This provides for a higher degree of security on the file server.

## Licence manager options

The licence manager can be accessed by clicking with the right mouse button on the FastReact task bar icon. This will present a menu with the following options

- Configure the licence server
- Start
- Stop
- View log (not available if running as a service)
- Exit
- Configure the licence server

The installation of the Service and Manager, under normal circumstances, will be carried out by Fast React Systems Implementer or Agent.

## Licence file (.frl)

This data on this file will be the Licence Options sold to the client, the client database serial number and an expiry date. Without this file users will be unable to access FastReact.

## Licensed database

This is the database as defined in the Licence Server program. Only licensed databases can be used with FastReact. Licence information is held in a variety of tables and is protected by encryption and other internal checks. Do not modify the contents of the database from outside of FastReact as this could invalidate your licence system.

## FastReact

FastReact will only run against a licensed database. If the database is not licenced then FastReact will issue a notification and then terminate.

## Normal operation

Under normal circumstances the licensing system is totally transparent to the FastReact user. The only time that a user would become aware of its existence if they try to exceed licensed limits such as the number of concurrent users or the maximum allowed number of planning board rows.

## What if something goes wrong

There are a number of things that can go wrong with any system and to protect against this we have provided for an emergency system to keep you going.

Problems could include loss of theft of the Licence Key. Note that you are responsible for the safe keeping of the key and Fast React Systems Ltd will want to make a charge for its replacement. Alternatively it could fail electrically (this is very rare). Such keys will be replaced at no charge on the return of the faulty key to Fast React Systems Ltd.

If something goes wrong then FastReact will give you the option of entering an emergency code. This code will reinstate your licence but only for 30 days. This is to allow sufficient time for your permanent licence to be corrected.
