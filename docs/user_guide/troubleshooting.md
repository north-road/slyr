# Troubleshooting #

## Error Messages ##
 Error Message | Rectification |
 ------------- | ------------- |
 Group transparency was converted to individual layer transparency (group transparency requires QGIS 3.24 or later) | Update your QGIS to QGIS 3.24 or later |
 Raster layers in Geodatabase files are not supported in QGIS, the database X:\folder\geodatabase.gdb\raster.gdb will need to be converted to TIFF before it can be used outside of ArcGIS | Convert all rasters sitting within the GDB as TIFFs
 Raster catalog layer “RasterLayer” has been removed from the project (raster catalog layers are not supported by QGIS)| These layers will need to be created seperately outside of the catalog layer before conversions.
 

## Add in SVG files ##
If you have access to the SVG files you need, and you find that SLYR is not bringing them in, check to see if the location is listed in the `Settings` ▶️ `Options` ▶️  `SVG Paths`. 
![SVG Paths](../images/svg_paths.png)

## Reinstall my SLYR Plugin ##
If you have changed machines, you may need to reinstall the **SLYR** Plugin. 

1. Navigate to the SLYR Plugin folder you were sent. 

2. Grab the .py and drag and drop it over your QGIS. 

3. Open the `QGIS Plugin Manager`

## Update my SLYR licence ##
**SLYR** is updated regularly and **QGIS** will let you know when a new version has been released. To update your version:

1. Open the **Plugin Manager**, click on the top menu item `Plugins` ▶️ `Manage and Install Plugins`.

![Open Plugin Manager](../images/plugin_mngr_open2.png)

2. In the left panel, click on `Upgradeable` 

3. In the central panel, click on `SLYR`. If `SLYR` is not in the middle panel, then you should be up-to-date. 
> Check-out what has been updated in the *Changelog*.

3. On the lower right, click on `Upgrade Plugin`. Once upgraded, click on `Close`.

![Update SLYR](../images/upgrade.png)
> If you receive an error after the Plugin update indicating it wasn't able to upgrade, restart QGIS. If it still hasn't been upgrade, send us an email. 

