# Troubleshooting

## Cannot download SLYR from link

If you cannot download SLYR from the link provided, first try a different browser, including Chrome and Firefox. If this does not work, please contact us.  

If you find you get the `401 Unauthorized` page this may indicate that your organization has blocked access. Therefore, you will need to contact us for further installation requirements.

**Please contact us at <info@north-road.com> and we will respond as soon as we can (with the caveat that we are in AEST time zone).**

## You are asked for user credentials

If you are asked for your Username and Password when updating your plugin:

- Try re-running the installation routine from the welcome email (it's safe to re-run this over an existing SLYR install)
- Try installing SLYR using a new QGIS [User Profile](https://docs.qgis.org/latest/en/docs/user_manual/introduction/qgis_configuration.html#working-with-user-profiles)

If this does not fix the problem, please contact us at <info@north-road.com> and we will help you to reinstall.

## Warnings during conversions

During document conversion SLYR will raise warnings describing any properties from the
document which cannot be automatically converted. The table below describes some of
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

## Annotations and Annotation Classes

Annotations serve many different use cases in ESRI software. Depending on what
type of annotation or annotation class you are converting and what your requirements
are, SLYR offers a number of tools to meet your needs.

If you are converting:

- Text annotations stored in a File GeoDatabase annotation class, and want the
  result to be reusable across different projects, you should use the "Convert
  Annotation Classes to Geopackage" tool
- Text annotations stored in a File GeoDatabase annotation class, and just want
  the results added to the current project, you should use the "Convert
  Annotations" tool
- Graphical or text annotations which are stored in an ArcGIS Project file (eg
  a MXD, LYR, APRX, LYRX file) and the underlying data source is NOT a File
  GeoDatabase annotation class, then use the corresponding tool for converting
  this document type should be used. (E.g. Convert MXD to QGS).

## Data Frames

If you have more than one data frame in your ESRI product, QGIS will bring it is as a new group layer. Slyr also creates a map themes for each data frame and configures the print layouts to read to these map themes.

## Fonts

When converting ArcMap or ArcGIS Pro documents, you will need to have all
fonts referenced by the documents installed on your system. If any fonts are
not available, SLYR will display warnings listing all missing fonts.

For best conversion results you should source these missing fonts and install
them on the system.

## GeoDatabases

### Missing or invisible features

If some features do not display from GeoDatabase layers, there may be an error with the
Geodatabase Layer's Index.

> **Workaround:**
>
> - In **ArcGIS Pro**, open the GDB file in the `Catalog`.
> - Under the `Indexes` tab, choose whether to rebuild the index, remove or
    re-create it.
> - Rerun the **SLYR** tool.

### Personal GeoDatabases (MDB/PGDB)

If you are running **Windows**, you may come across some issues with the
conversion of Personal GeoDatabases (PGDB). Some manual configuration is
needed before these can be opened within QGIS. You may need administrative
rights on your computer in order to complete these steps.

> **Fix:**
>
> - Download and install the 64-bit version of the ODBC driver
    from [Microsoft](https://www.microsoft.com/en-gb/download/details.aspx?id=13255)
>
> If you don't have a 32-bit version of office installed you can just run
> the executable. If, however, you do have a 32-bit office installation you
> will
> need to run the executable from a command prompt using the "/passive" argument.

### Raster GeoDatabase Layers

Support for raster layers from GeoDatabases was recently introduced in QGIS.
Please ensure that you have  QGIS v3.30.3 or v3.28.7 (or later) to enable this
support.

### Raster Catalog Layers

These are not supported in any QGIS version, and will be omitted from any converted documents.

### Export Data to Geodatabase

QGIS has inbuilt support for many more files than are supported in ArcGIS Pro.
When exporting a QGIS project for use in ArcGIS Pro, you may first need to
convert some layer data sources to an ESRI readable format. We suggest exporting
the data to File GeoDatabases for best compatibility with ESRI software.
You can either export data to a new GeoDatabase, or to an existing
GeoDatabase (go from step 3 below).

![Create GDB in QGIS](../images/gdb_create.png)

1. In the QGIS Browser window, right-mouse click the folder you wish to create
   the geodatabase in and click on `New` ▶️ `ESRI FileGeodatabase`.
2. Type in the name of the geodatabase
3. Find and select the layers you wish to export to the GeoDatabase.
4. Drag and drop the selected layers onto the new GeoDatabase.
5. Repath the layers in your QGIS project to point to the exported GeoDatabase
layers (right-mouse click the layer and click on `Change Data Source`).

## LYR files

### Repairing Data Sources

When you convert ESRI documents using **SLYR** and
the `Repair data source`![Repair data source](../images/repair_data_source.png)
icon appears next to the data, this means the path to the data is broken and
will need to be manually repaired.

![Repair LYR files](../images/LYR_repair2.png)
> There's a number of possible causes for this, but ultimately it means that
> QGIS can't find the data files referenced by the ESRI file. For instance:
>  * The data has been moved.
>  * The data no longer exists.
>  * The ESRI file has relative paths to the data files (eg
     .\transport\roads.shp), yet the converted QGIS file wasn't saved to the
     same location as the original ESRI file. We recommend always placing the
     converted QGIS files into the same folder alongside their original ESRI
     counterparts for best results.
>
> **Workaround:**
>
> Click the `Repair data source`![Repair data source](../images/repair_data_source.png) icon
> next to each layer and point the layer to the correct location of the dataset.

## Nested Joins

A nested joins is when table A is joined to table B which is itself joined to
table C. These are currently not supported by SLYR.

## Symbology

The following are some issues you may encounter during conversions of symbols.

### Marker Symbols

Marker halos are not supported in QGIS, as there's no way in current QGIS
versions to achieve the same effect. During conversion SLYR will ignore
the marker halo setting, and you may need to adjust your symbology accordingly.

## Reporting Bugs

If a tool is not working, we apologize that this is impacting your workflow! If
it is a bug, we will rectify as soon as possible.

> **Workaround:**
>
> - If you are using the fully licensed **SLYR**, [email us](mailto:info@north-road.com) immediately with as much as
    detail
    as possible including the files. We will look into the bug and get back to
    you with a solution. Once solved, we will push up a new version to the QGIS
    Plugin Manager with all the fixes.
> - Check if you are using the Community Edition or the Licensed Edition of **SLYR**.
    If you are using the Community Edition, then the tool is not yet
    available in the license version. Please note that we don't offer any direct
    support for the Community Edition.
