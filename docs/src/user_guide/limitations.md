# Known Limitations

SLYR will always follow the development in **ESRI** and **QGIS** to provide
conversion opportunities as they arise, but if non-compatibility exists, then
conversions are limited. But don't be disheartened, if the ability is in ESRI,
we can always develop it within QGIS. The other way around though - well that
is out of our hands, and workarounds may be attempted.

To be transparent, we have listed the current limitations that we know of, what
we are doing about it and if there is a workaround in the meantime.
> If you know a limitation that isn't listed,
> please [email us](mailto:info@north-road.com) and we will investigate it.

<!--## Template ##
Description
> Workaround intro

1. Instruction
2. Instruction

> Proposed solution: currently working on it -->

## Geopackages

Whilst we are love our neat geopackages in QGIS, ESRI is yet to deliver on this
functionality. If you are going from QGIS to ESRI, you will need to save as a
shapefile or a geodatabase.
> Workaround:
> See [Geopackages Troubleshooting](https://slyr.north-road.com/user_guide/troubleshooting/#geopackage)
>
> Proposed solution: ESRI geopackage development

## Graduated renderer

SLYR cannot translate a QGIS graduated renderer to any comparable result in
ArcGIS Pro if there's any gaps within the class ranges as ArcGIS Pro does not
support gaps.
> Workaround: this is pretty easy

* Correct the class breaks from the QGZ project to remove the gaps between the
  classes.

> Proposed solution: currently working on it

## Label Class disabled in ArcGIS Pro

When using the QGS to MAPX tool, the Label Class options are disabled in ArcGIS
Pro.
> Workaround: tbc
>
> Proposed solution: currently working on it

## Legend Text

- Wrapped legend text is currently not supported.

## QGIS to MXD

SLYR does not offer assistance in transforming QGIS projects into MXD. However,
it does support the conversion of QGIS projects to newer ArcGIS Pro formats
like LYRX, MAPX, and APRX. Since ArcMap is undergoing phased-out development,
slated to end in March 2026, SLYR has concentrated its conversion efforts on
ESRI formats with assured future support and maintenance. Consequently, the
development of a QGIS to MXD conversion tool is not being pursued. Given the
available alternatives of using either QGIS or ArcGIS Pro for similar tasks,
dedicating resources to this particular undertaking is currently deemed
impractical.

> Proposed solution: unless you transition to supported formats like QGIS,
> regrettably, your only alternative is to reconstruct the project within ArcMap.

## Raster Catalog Layers

A Raster catalog is a feature of ArcMap. Its ArcGIS Pro equivalent is mosaic
datasets.
In QGIS there is currently no equivalent to Raster Catalog Layers. Any of these
layers will be skipped over in the process and omitted from the project.

> Workaround should only be used if you require the symbology for the raster.

* Extract the required layers within the Raster Catalog as raster layers.

> Proposed solution: there is no proposed solution as the data sits as a
> temporary layer within a project. Additionally, Raster Catalogs are a feature
> within ArcMap which is being phased out.

## Rasters in GDB

Raster layers that are contained in GDB are currently not supported in QGIS.

> Workaround:

* Extract the rasters from the GDB if the symbology is required in QGIS

> Proposed solution: waiting on GDAL to develop the ability to read rasters in
> GDB.

## Rule-based renderers

One of our favourites features of **QGIS** Symbology is the ability to create
efficient cartography through the use of Rule-Based renderers (Rule-Based
classification symbology). There is currently no direct equivalent in ArcGIS
Pro. Therefore, if your **QGIS** project has many layers based on rule-based
classifications, try this for a workaround.
> Workaround: Painful - yes, Inefficient - yes - but let's manually capture the
> rule-based classification in the layer's field.

1. In **QGIS**, open up a layer's `attribute table`.
2. Create the number of fields required to record each rule-based
   classification against the features.
3. Select the fields according to your filter used in the rule-based
   classification.
4. Populate the fields with the name of your rule-based classification.
5. Save your edits.
6. In the `layer panel`, duplicate the layer and name it according to the
   rule-based classification.
7. Apply the symbology to each layers as per the rule-based classification.

> Proposed solution: still looking for one.

## SLD to LYR/LYRX

These tools do rely entirely on QGIS' SLD export capabilities, so the quality
of the conversion will depend on the symbology options used in the ArcMap
documents and how compatible they are with QGIS' SLD support. The SLD format
itself has considerably less symbology functionality compared with either QGIS
or ArcMap, therefore a conversion to SLD will often be a lossy process,
dropping complex options back to simpler SLD supported symbology.
> Workaround:

* Reasses symbology choices in ArcMap

> Proposed solution: will improve with QGIS' SLD capabilities. If this is a
> major issue, consider funding the capability development of it.

## SVG Markers

Warning: Water: QgsSvgMarkerSymbolLayer symbol layers cannot be converted yet
> Workaround: remove the SVG Marker or save it to import into ArcGIS Pro

> Proposed solution: currently working on it

## Vector tile packs - Index

There are two types of Vector Tile Packs (VTPK) in **ESRI**:
Flat : supported by **SLYR**
Index: not supported **SLYR**

> There is no workaround for this limitation.

> Proposed solution: waiting for funding and demand by the community to develop
> it.

## Urgent fixes

If you have a large project impacted by limitations that requires an urgent
fix, [contact us](mailto:info@north-road.com) here at **North Road** and we
could look at a number of options.

- Undertake the conversion for you. This may attract a small fee, dependent on
  the work, but please ask.
- You could fund the development of the solution to go into the tool for all
  and become a member of our [Hall of Fame](hall_of_fame)

> By asking us, you are letting us know of the limitation and by delivering a
> solution for you, it may help develop a solution for all in the tool. 

