# Automated Installation / Upgrade for FastReact Licencing

**Source:** FastReact Help (version 4.44) — Technical information
**Menu path:** Automated Installation / Upgrade for FastReact Licencing > Print View

---

The new FR Licence package will allow the Fast React Implementer to install the Fast React Licence software automatically via the downloaded Installation Package.

The Installation Package contains:

- Sentinel Dongle Software
- Sentinel Cloud Drivers
- FR Licence Manager
- FR Licence Service

## The Installation Process

*Context: Automated Installation / Upgrade for FastReact Licencing > Print View › The Installation Process*

The FR Licence Package will be made available to FR personnel and to clients upon request. The installation of this Package should ideally only be done by an FR employee, as it does require some understanding of the Licencing process.

Setup - FR Licence

Once downloaded, right click on the FR_Licence.exe and select “Run as Administrator”. This will start the installation:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 04 01 rot]

Click on the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 04 02 rot]

Accept the Licence Terms and then click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 05 01 rot]

Enter the Installation Password. This code will be provided to you by the UK Support Desk. Click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 05 02 rot]

Read the instruction and prerequisites and when done click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 06 01 rot]

For systems with existing FR Licence installations, browse to the location of the FR Licence files. For new FR Licence installations browse to the desired installation location. Click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 06 02 rot]

Systems with an existing FR Licence folder will be asked to confirm the installation location, click the Yes button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 07 01 rot]

Click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 07 02 rot]

Check that you are happy with the Destination Directory and click the Install button to start the installation:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 08 01 rot]

The installation will take a couple of minutes. You will then be presented with an options screen to install Drivers and Run the FR Licence Service Installer:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 08 02 rot]

- READ ME FIRST.txt - this file just has a few pointers in case of any issues with the installation of either Dongle or Cloud drivers
- Run Sentinel System Driver Installer - (this is now called Sentinel Protection Installer), this will start the process of installing the Dongle Drivers
- Run haspdinst.exe
 - this will install the Cloud Dongle Drivers
- Run FRLINST.exe
 - this will install the FastReact Licence Manager and Service

Unticking any one of these options will prevent that part of the installation from happening and will mean that manual installation will need to be done.

### Sentinel Protection Installer

*Context: Automated Installation / Upgrade for FastReact Licencing > Print View › The Installation Process › Sentinel Protection Installer*

The next step that will happen will be the automatic installation of the Sentinel Dongle Drivers.

As soon as the Setup stage has finished the FR Licence Installer Package will install or upgrade the Sentinel Dongle Drivers:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 09 01 rot]

Click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 10 01 rot]

Accept the Licence Terms, and click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 10 02 rot]

Select the Custom option, and click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 11 01 rot]

Right click on Sentinel Protection Server, and select the option to NOT install this option. Do the same for Sentinel Keys Server and Sentinel Security Runtime.

Ensure that both Parallel Driver and USB System Driver are enabled and set to install.

Click the Next button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 12 01 rot]

The Sentinel Drivers are now ready to install. Click the Install button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 12 02 rot]

Once the Sentinel Driver installation is complete, click the Finish button.

The Sentinal Dongle Drivers have now been installed on the Server. The FR Licence installation will now install the Cloud Dongle Drivers.

### Sentinel Cloud Dongle Installer

*Context: Automated Installation / Upgrade for FastReact Licencing > Print View › The Installation Process › Sentinel Cloud Dongle Installer*

It may appear that there is nothing happening now, however, the Sentinel Dongle Drivers are being installed. Please be patient as it may take a minute or two before you see the screen below:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 13 01 rot]

This process will take a couple of minutes to run. You will then be informed that the Operation was successfully Completed:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 13 02 rot]

Sentinel Cloud Dongle Drivers have now been installed.

### FRLINST - FR Licence Manager and Service

*Context: Automated Installation / Upgrade for FastReact Licencing > Print View › The Installation Process › FRLINST - FR Licence Manager and Service*

The final stage is the installation or upgrade of the FR Licence Manager and FR Licence Service. The FRLINST program will automatically detect if the FastReact Licence Service in installed and running and will prompt you if you are installing the new FR Service in a different location:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 13 03 rot]

It is very strongly recommended that you install FR Licence

to the same location as the existing location.

Click the No button here and correct your installation location.

If the FR Licence software is being upgraded, the FRLINST program will stop the currently running FR Licence Service:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 14 01 rot]

Click the Yes button:

[Screenshot: W SOP Automated Installation and Upgrade for FastReact Licencing 14 02 rot]

FRLINST will stop the current FR Licence Service running, uninstall it, and then install the new versions of the FR Licence Manager, FR Licence Service, and the SafeNet Sentinel Cloud Services. It will then restart the FR Licence Service.

#### Next stage:

*Context: Automated Installation / Upgrade for FastReact Licencing > Print View › The Installation Process › FRLINST - FR Licence Manager and Service › Next stage:*

Configure the FR Licence Manager. [Fast React Licence Installation Guide](http://frs-wiki/dokuwiki/doku.php?id=fr_licenceing:installing_fastreact_licence:troubleshoot)

Configure Cloud Licencing. [Fast React Cloud Licencing](http://frs-wiki/dokuwiki/doku.php?id=fr_licenceing:cloud_licencing:cloud)
