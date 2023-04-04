# Set-up SLYR #
<!-- it would be nice to only give access to this page to purchasers -->

## Install the plugin (community version) ##

The community version of SLYR can be installed through the QGIS Plugin Manager. Just search for "SLYR" and click "Install Plugin".

## Install the plugin (licensed version) ##

Once purchased, licensed users will receive an email from **North Road** with a link for the installer and their licence key. 

**Before installing the licensed version of SLYR, you must first uninstall the community version (if installed) and restart QGIS.**

1. Save the information in this email, along with your invoice and receipt in a safe place for future reference.

2. Download the installer from the link. 
      * Place the zip file in a safe location for future reference - just in case you need to update your machine so you can reload it.

3. Unzip the downloaded file, and then drag the extracted `install_slyr_qgis.py` over an open **QGIS** window. (If prompted, accept the warning regarding trusted scripts). The script will add a connection to the private plugins repository, and install the **SLYR** plugin for you.

4. After the plugin is installed, the **SLYR** `Options` dialog will open (If it doesn't, click on the top menu `Settings` ▶️ `Options` and click on **SLYR** in the left panel). Enter your unique license key at this screen, exactly as it appears at the end of this email. Enter the optional requirements outlined in the *SLYR Options* section below.

## SLYR Options ##
The **SLYR** `Options` dialog provides users the ability to set-up the **SLYR** Plugin to meet their requirements. 

To access the **SLYR** `Options`, in **QGIS** click on the top menu `Settings` ▶️ `Options`.

![Settings Options](../images/settings_options.png)

The `Options` dialog opens, scroll down on the left and click on **SLYR** to access the **SLYR** options.

![SLYR Options](../images/settings_options_slyr_edit2.png)

### Plugin Settings ###
| Setting | Description | Directions |
| ---| --- | --- |
|License key | The license key is supplied to users once they have purchased **SLYR**. | Enter your unique license key at this screen, exactly as it appears at the end of this email.|
|Experimental annotation support | Annotation support is currently in Beta testing. If you would like to partake in the testing, tick this option. Any issues, please send us an [email](mailto:info@north-road.com). <NYALL IS THIS ONLY FOR COMMUNITY EDITION? WHAT DOES THIS DO?> |  Tick to activate. |
|Verbose logging during conversion | Activate the developer version of the plugin. This will record more details and assist with future developement. However it can slow down performance. | Tick to activate. |

### Conversion Settings ###
| Setting | Description | Directions |
| ---| --- | --- |
Convert font markers to simple marker symbols where possible | All Symbol marker symbols will loose any complexity. WILL THIS MIRROR THE CHOSEN SYMBOLS CLOSELY? WILL IT LOSE ALL COLOUR AS WELL? |  Tick to activate. 
Convert font markerts to SVG files | Use this option if you have access to the original SVG files and they are saved in.  |  Tick to activate. Ensure the location is addded into the **QGIS** `Options` dialog (check [Troubleshooting](/user_guide/troubleshooting) for more information).
Embed pictures inside symbols when possible | Symbols containing pictures are assumed to have placement inside symbols. If your pictures occur outside of symbols, don't activate this option. IS THIS CORRECT???? |  Tick to activate. 
Tweak symbol conversion for better visual match | A variety of scripts can be employed to get a better match, such as PROVIDE EXAMPLES OR FURTHER CLARIFICATION> |  Tick to activate. 
Units for symbols: points, millimeters | Symbols use points or millimeters to measure them. **SLYR** uses points as a default. |  Choose either `Points` or `Millimeters`.
Store extracted pictures in | Pictures are extracted and processed using Inkscape. The files will then need a storage location. WHAT PICTURES ARE TALKING ABOUT - FROM SYMBOLS OR PHOTOS LINKED IN THE PROJECT |  Enter in the folder's path
Store relative paths for files instead of absolute paths | Using relative paths will assist with portability of the project. |  Tick to activate. 

### SDE Database Conversion ###
| Setting | Description | Directions |
| ---| --- | --- |
Default primary key | Default value is OBJECTID, but this can be changed as per requirements | Leave as OBJECTID or amend as required. 
Table name conversion | An option to amend how the table's name is written <WHAT WAS THE REASON FOR THIS - OCD TO CLEAN IT UP ;) WHICH IS A GOOD THING>  | Choose from the options: Leave unchanged, Convert to Uppercase, OR Convert to Lowercase

### MDB Tools ###

| Setting | Description | Directions |
| ---| --- | --- |
Path to MDB Tools | This is automatically set for the full license, *only the Community License needs to download this tool*. The MDB tools is required for conversion of ESRI .style databases. | Click the link in the SLYR Options dialog and once downloaded, enter in the path

### Inkscape ###
| Setting | Description | Directions |
| ---| --- | --- |
Path to Inkscape | Inkscape is required to assist in the conversion of .svg and other images.  |  Install Inkscape from [here.](https://inkscape.org) and enter the pathway to Inkscape .exe file.
