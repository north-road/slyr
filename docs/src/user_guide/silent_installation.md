## Silent Installations

A silent install is used to install an application without the need to interact with the UI. This type of installation is helpful for applications with limited installation steps. There are a number of approaches which can be used to silently install SLYR, with the recommended approach varying depending on how QGIS itself is deployed within an organisation.

A common approach is to package up a "template" QGIS user profile, and deploy that along with the organisation's QGIS installation package or script. A user's QGIS settings are all stored within the %AppData%\QGIS\QGIS3\profiles\default path.

To create a template profile:

1\. Run QGIS, install the SLYR plugin (and any other default plugins you want deployed to your users), and change any default QGIS options as desired.

2\. ZIP/package up the resultant %AppData%\QGIS\QGIS3\profiles\default folder, including the %AppData%\QGIS\QGIS3\profiles\default\python\plugins\slyr folder.

3\. As part of your QGIS installation script, extract the default user profile into the user's %AppData%\QGIS\QGIS3\profiles\default folder.

If you are not copying the QGIS settings ini as part of the deployment, then you will also need to set the SLYR license key the user's QGIS profile. This can be done programatically by calling a Python command:

    QgsSettings().setValue('/plugins/slyr/license', 'your license key value')

See the \[QGIS Documentation]\(<https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/intro.html#the-startup-py-file>) for instructions on how a Python command can be run automatically at QGIS startup.
