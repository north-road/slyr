# Troubleshooting #

## Error Messages ##

 Error Message | Rectification |
 ------------- | ------------- |
 Converting CIMBackgroundCallout not implemented yet | In ArcGIS Pro, remove all background items from the label as the layer will not be converted
 Converting CIMCompositeCallout not implemented yet | In ArcGIS Pro, remove all background items from the label as the layer will not be converted
 Converting .gpkg layers is not yet fully supported, layer path has been replaced with a dummy shapefile path | Convert your geopackages into a GDB or a SHP
 Group transparency was converted to individual layer transparency (group transparency requires QGIS 3.24 or later) | Update your QGIS to QGIS 3.24 or later |
 QgsSvgMarkerSymbolLayer symbol layers cannot be converted yet | Amend layers that contain a QGIS SVG Marker as they will not be converted.  
 Raster layers in Geodatabase files are not supported in QGIS, the database X:\folder\geodatabase.gdb\raster.gdb will need to be converted to TIFF before it can be used outside of ArcGIS | Convert all rasters sitting within the GDB as TIFFs
 Raster catalog layer “RasterLayer” has been removed from the project (raster catalog layers are not supported by QGIS)| These layers will need to be created seperately outside of the catalog layer before conversions.
 Warning: Detailed Surface geology: Could not automatically convert Arcade expression: $feature. Please check and repair this expression | This will happen if the Arcade expression in the labelling class has not been completed. Fix by assigning a field to the $feature
 Unique Value legend group title “Lead (206/204 min)” is not supported by QGIS | TBC
Warning: IOGP3004 Sand Ripples: Font Vrinda not available on system | LYR requires all the fonts referenced by an ESRI document to be installed on the system performing the conversion for best results. Load a legal copy of the font and place it in your systems fonts library i.e. C:\Windows\Fonts 
 
<!---
## heading ##
Issue 
> Impact
 >  - impact
 >  
> **Workaround:** 
 > 
 > - Instruction
--->

## Annotations ##
Annotations are on our roadmap! 
The good news: if your annotation was created in ArcMap, SLYR can convert it. 
The not-so- good news: annotations created in ArcGIS Pro have changed and we are still working on creating this tool. 


## Fonts ##
The font is not coming into the conversion or you get an error message at the top that the font is not recognised. 
> **Workaround:** 
 > 
 > - Find a legal copy of the font and place it in your systems fonts library i.e. C:\Windows\Fonts 


## Geodatabases ##
### Indexes
If polyline and point feature classes do not display despite them appearing in the layer window of the resulting QGS project, there may be an error with the Geodatabase Layer's Index. 
> **Workaround:** 
 > 
 > - In **ArcGIS Pro**, open the GDB file in the `Catalog`.
 > - Under the `Indexes` tab, choose whether to rebuild the index, remove or re-create it.
 > - Rerun the **SLYR** tool.

### Raster conversion ###
Please ensure that you have the QGIS v3.30.3 or v3.28.7 to enable this function. 
> **Workaround:** 
 > 
 > - In **ArcGIS Pro**, convert to geotiff.
>  - Run SLYR again.

### Raster Catalog ###
This is not supported in QGIS and will be omitted from the project.

## Geopackage ##
ArcGIS Pro and Geopackages has not yet reached full support. Therefore an error will be produced if you are exporting from a geopackage 
e.g. *Warning: Feature: Converting .gpkg layers is not yet fully supported, layer path has been replaced with a dummy shapefile path*

>  If your files are in a geopackage, ArcGIS Pro will not recognise this and the following may happen:
  > 
  >  - The file links will be broken
  >  
  >  - If you repath them to the geopackage, this will impact on the symbology. 
>
> **Workaround:** Export to geodatabase or shapefile

### Export to Geodatabase ###
You can export geopackage data to a new geodatabase or to an existing geodatabase (go from step 3 below).

![Create GDB in QGIS](../images/gdb_create.png)

1. In the QGIS Browser window, right-mouse click the folder you wish to create the geodatabase in and click on `New` ▶️ `ESRI FileGeodatabase`.
2. Type in the name of the geodatabase
3. In the geopackage, select the layers you wish to add to the geodatabase.
4. Drag and drop the selected layers onto the new geodatabase.
5. Repath your data to the shapefiles (right-mouse cick the layer and click on `Change Data Source`.

### Export to shapefile ###
If you have many shapefiles, install the **Bulk Vector Export** plugin.

![Bulk Vector Export](../images/bulk_vector_export.png)

1. Ensure all the files you wish to export are active (tick them on).
2. Select the output format 'ESRI shapefile`.
3. Select the CRS you wish to export them with.
4. Click on OK.
5. Repath your data to the shapefiles.

## Group Transparency ##
Need QGIS 3.24 or later.

## LYR files ##
### Repair Data Source ###
When you load in your LYR files using **SLYR** and the `Repair data source`![Repair data source](../images/repair_data_source.png) appears next to the data, this means the pathway is broken. 

![Repair LYR files](../images/LYR_repair2.png)
> There's  a number of possible causes for this, but ultimately it means that QGIS  can't find the data files referenced by the LYR file. (LYR files don't  contain any actual data themselves, just links to where data is stored  elsewhere)
 >  * The data has been moved.
 >  * The data no longer exists.
 >  * The LYR file has relative paths to the data files (eg  .\transport\roads.shp), and the converted QGIS file wasn't saved to the  same location as the original LYR file. When relative paths are used, then the QGIS files must be saved alongside their original counterparts for these relative paths to point to the correct locations.
 >   >  
> **Workaround:** 
 > Find the location of the files and point the layers to this source. 


## Reinstall my SLYR Plugin ##
If you have changed machines, you may need to reinstall the **SLYR** Plugin. 

1. Navigate to the SLYR Plugin folder you were sent. 

2. Grab the .py and drag and drop it over your QGIS. 

3. Open the `QGIS Plugin Manager`

## SVG ##
### Add in SVG files for QGIS ###
If you have access to the SVG files you need, and you find that SLYR is not bringing them in, check to see if the location is listed in the `Settings` ▶️ `Options` ▶️  `SVG Paths`. 
![SVG Paths](../images/svg_paths.png)

### Add in SVG files for ArcGIS Pro ###
QGIS SVG Markers are not yet supported for conversion into ArcGIS Pro. They are however on the list to be supported. 
> **Workaround:** 
> 
> - Remove any svg layers in your layer's symbology. In ArcGIS Pro choose the appropriate style. 
> 
> - If the SVG are unique and required, import them to a style using the [ImportSVGsToStyle](https://carto.maps.arcgis.com/home/item.html?id=c25ab2da6ae343af9acc632120c7cf01){:target="_blank" rel="noopener"}_ ArcGIS Pro Add-In by DStephen_carto.

## Tool not working ##
If a tool is not working, we apologise that this is impacting your workflow. If it is a bug, we tend to try and fix this, historically, quite quickly.
> **Workaround:** 
>
> - Check if you are using the Community Edition or the Full Licence of **SLYR**. If you are using the Community Edition, then the tool is not yet available in the licence version. 
> - If you are using the fully licenced **SLYR**, send us an [email](mailto:info@north-road.com) immediately with as much as detail as possible including the files. We will look into the bug and get back to you with a solution. Once solved, we will push up a new version to the QGIS Plugin Manager with all the fixes. 


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

