# Troubleshooting

## Warnings during conversions

During document conversion SLYR will raise warnings describing any properties
from the
document which cannot be automatically converted. The table below describes
some of
these warnings, and how they can be handled:

 Warning                                                                                                            | Rectification                                                                                                                                                                                                             |
 --------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
 Group transparency was converted to individual layer transparency (group transparency requires QGIS 3.24 or later) | Update your QGIS to QGIS 3.24 or later                                                                                                                                                                                    |
 Raster layers in Geodatabase files are not supported in QGIS                                                       | Update to a newer QGIS version for raster GeoDatabase support.                                                                                                                                                            |
 Raster catalog layer has been removed from the project (raster catalog layers are not supported by QGIS)           | These layers will need to be created separately outside of the catalog layer before conversions.                                                                                                                          |
 Could not automatically convert expression. Please check and repair this expression.                               | A label or filter expression from the ESRI document could not be automatically converted to a QGIS expression. The layer will need to be modified and the expression manually converted to a QGIS equivalent by the user. |
 Unique Value legend group title is not supported by QGIS                                                           | This is a warning that the group title has been dropped in the QGIS layer. Legend text may need to be manually updated accordingly.                                                                                       |
 Font XXX not available on system                                                                                   | See [fonts](#fonts)                                                                                                                                                                                                       |
 Class Break legend group title is not supported by QGIS                                                            | This is a warning that the group title has been dropped in the QGIS layer. Legend text may need to be manually updated accordingly.                                                                                       |
 X: Marker halos are not supported by QGIS                                                                          | The option used in the MXD isn't possible to match in current QGIS versions. In this case a warning is raised and the rest of the layer's properties are converted.                                                       |
 Mosaic layer has been removed from the project (Mosaic layers are not supported by QGIS)                           | This relates to a Mosaic layer in the MXD document -- current QGIS versions don't have any way of opening these so we skip over them during the conversion.                                                               |

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

## Annotations

If you are converting:

- Text annotations stored in a File Geodatabase annotation class and want the
  result to be reusable across different projects, you should use the "Convert
  Annotation Classes to Geopackage" tool
- Text annotations stored in a File Geodatabase annotation class and just want
  the results added to the current project, you should use the "Convert
  Annotations" tool
- Graphical or text annotations which are stored in an ArcGIS Project file (eg
  a MXD, LYR, APRX, LYRX file) and the underlying data source is NOT a File
  Geodatabase annotation class then use the corresponding tool for converting
  this document type

## Fonts

When converting ArcMap or ArcGIS Pro documents, you will need to have all
fonts referenced by the documents installed on your system. If any fonts are
not available, SLYR will display warnings listing all missing fonts.

For best conversion results you should source these missing fonts and install
them on the system.

### Curved text

Curved text is supported from QGIS 3.32 version onwards.

## GeoDatabases

### Indexes

If polyline and point feature classes do not display despite them appearing in
the layer window of the resulting QGS project, there may be an error with the
Geodatabase Layer's Index.
> **Workaround:**
>
> - In **ArcGIS Pro**, open the GDB file in the `Catalog`.
> - Under the `Indexes` tab, choose whether to rebuild the index, remove or
    re-create it.
> - Rerun the **SLYR** tool.

### Personal GeoDatabases (MDB/PGDB)

If you are running **Windows**, you may come across some issues with the
conversion of Personal GeoDatabases (PGDB). Don't worry, there is a fix for
this. You may need Admin rights on your computer.
> **Fix:**
>
> - Download the 64-bit version of the ODBC driver
    from [Microsoft](https://www.microsoft.com/en-gb/download/details.aspx?id=13255)
>
> N.B. If you don't have a 32-bit version of office installed you can just run
> the executable. If, however, you do have a 32-bit office installation you
> will
> need to run the executable from a command prompt using the /passive option

### Raster conversion

Please ensure that you have the QGIS v3.30.3 or v3.28.7 to enable this
function.
> **Workaround:**
>
> - In **ArcGIS Pro**, convert to geotiff.
    >

- Run SLYR again.

### Raster Catalog

This is not supported in QGIS and will be omitted from the project.

### Export to Geodatabase

You can export geopackage data to a new geodatabase or to an existing
geodatabase (go from step 3 below).

![Create GDB in QGIS](../images/gdb_create.png)

1. In the QGIS Browser window, right-mouse click the folder you wish to create
   the geodatabase in and click on `New` ▶️ `ESRI FileGeodatabase`.
2. Type in the name of the geodatabase
3. In the geopackage, select the layers you wish to add to the geodatabase.
4. Drag and drop the selected layers onto the new geodatabase.
5. Repath your data to the shapefiles (right-mouse click the layer and click
   on `Change Data Source`).

### Export to shapefile

If you have many shapefiles, install the **Bulk Vector Export** plugin.

![Bulk Vector Export](../images/bulk_vector_export.png)

1. Ensure all the files you wish to export are active (tick them on).
2. Select the output format 'ESRI ShapeFile'.
3. Select the CRS you wish to export them with.
4. Click on OK.
5. Repath your data to the shapefiles.

## Group Transparency

Need QGIS 3.24 or later.

## LYR files

### Repair Data Source

When you load in your LYR files using **SLYR** and
the `Repair data source`![Repair data source](../images/repair_data_source.png)
appears next to the data, this means the pathway is broken.

![Repair LYR files](../images/LYR_repair2.png)
> There's a number of possible causes for this, but ultimately it means that
> QGIS can't find the data files referenced by the LYR file. (LYR files don't
> contain any actual data themselves, just links to where data is stored
> elsewhere)
>  * The data has been moved.
>  * The data no longer exists.
>  * The LYR file has relative paths to the data files (eg
     .\transport\roads.shp), and the converted QGIS file wasn't saved to the
     same location as the original LYR file. When relative paths are used, then
     the QGIS files must be saved alongside their original counterparts for
     these relative paths to point to the correct locations.
>
> **Workaround:**
> Find the location of the files and point the layers to this source.

## Nested Joins

A nested joins is when table A is joined to table B which is itself joined to
table C, and this could go on. These are currently being developed for SLYR.

> **Workaround:**
> Open each of the file in QGIS and join one of the files to each other, keep
> the fields you need and export that out. Then join the additional files onto

## Reinstall my SLYR Plugin

If you have changed machines, you may need to reinstall the **SLYR** Plugin.

1. Navigate to the SLYR Plugin folder you were sent.

2. Grab the .py and drag and drop it over your QGIS.

3. Open the `QGIS Plugin Manager`

## Symbology

The following are some issues you may encounter during conversions of symbols.

### Marker Symbols

Marker halos are not supported in QGIS, as there's no way in current QGIS
versions to achieve the same effect. During conversion SLYR will ignore
the marker halo setting and you may need to adjust your symbology accordingly.

## Tool not working

If a tool is not working, we apologise that this is impacting your workflow. If
it is a bug, we tend to try and fix this, historically, quite quickly.
> **Workaround:**
>
> - Check if you are using the Community Edition or the Full Licence of **SLYR
    **. If you are using the Community Edition, then the tool is not yet
    available in the licence version.
> - If you are using the fully licenced **SLYR
    **, [email us](mailto:info@north-road.com) immediately with as much as
    detail
    as possible including the files. We will look into the bug and get back to
    you with a solution. Once solved, we will push up a new version to the QGIS
    Plugin Manager with all the fixes.

## Update my SLYR licence

**SLYR** is updated regularly and **QGIS** will let you know when a new version
has been released. To update your version:

1. Open the **Plugin Manager**, click on the top menu item `Plugins`
   ▶️ `Manage and Install Plugins`.

   ![Open Plugin Manager](../images/plugin_mngr_open2.png)

2. In the left panel, click on `Upgradeable`

3. In the central panel, click on `SLYR`. If `SLYR` is not in the middle panel,
   then you should be up-to-date.

   > Check-out what has been updated in the *Changelog*.

4. On the lower right, click on `Upgrade Plugin`. Once upgraded, click
   on `Close`.

![Update SLYR](../images/upgrade.png)
> If you receive an error after the Plugin update indicating it wasn't able to
> upgrade, restart QGIS. If it still hasn't been
> upgrade, [email us](mailto:info@north-road.com).
