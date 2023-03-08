# Limitations #
SLYR will always follow the development in **ESRI** and **QGIS** to provide conversion opportunities as they arise, but if non-compatibility exists, then  conversions are limited. But don't be disheartened, if the ability is in ESRI, we can always develop it within QGIS. The other way around though - well that is out of our hands, and workarounds may be attempted. 

To be transparent, we have listed the current limitations that we know of, what we are doing about it and if there is a workaround in the meantime. 
>If you know a limitation that isn't listed, please [email us](mailto:info@north-road.com) and we will investigate it. 

<!--## Template ##
Description
> Workaround intro

1. Instruction
2. Instruction

> Proposed solution: currently working on it -->

## Graduated renderer ##
SLYR cannot translate a QGIS graduated renderer to any comparable result in ArcGIS Pro if there's any gaps within the class ranges as ArcGIS Pro does not support gaps. 
> Workaround: this is pretty easy

* Correct the class breaks from the QGZ project to remove the gaps between the classes.

> Proposed solution: currently working on it 

## Raster Catalog Layers ##
A Raster catalog is a feature of ArcMap and it has been superseded by a mosaic dataset. Its ArcGIS Pro equivalent is mosaic datasets. 
In QGIS there is currently no equivalent to Raster Catalog Layers. Any of these layers will be skipped over in the process and omitted from the project.

> The workaround for this limitation is provide those layers within the Raster Catalog in a format that SLYR will read. If the intention is to mosaic many rasters together, use the Raster/Miscellaneous/Build virtual raster or other tools in this menu. 

> Proposed solution: there is no proposed solution as the data sits as a temporary layer within a project. Additionally, Raster Catalogs are a feature within ArcMap which is being phased out. 

## Rasters in GDB ##
Description
> Workaround intro

1. Instruction
2. Instruction

> Proposed solution: currently working on it -->


## Rule-based classification symbology ##
One of our favourites features of **QGIS** Symbology is the ability to create efficient cartography through the use of Rule-Based classifications. There is currently no direct equivalent in ArcGIS Pro. Therefore, if your **QGIS** project has many layers based on rule-based classifications, try this for a workaround. 
> Workaround: Painful - yes, Inefficient - yes - but let's manually capture the rule-based classification in the layer's  field. 



1. In **QGIS**, open up a layer's `attribute table`.
2. Create the number of fields required to record each rule-based classification against the features.
3. Select the fields according to your filter used in the rule-based classification.
4. Populate the fields with the name of your rule-based classification.
5. Save your edits.
6. In the `layer panel`, duplicate the layer and name it according to the rule-based classification.
7. Apply the symbology to each layers as per the rule-based classification.

> Proposed solution: still looking for one.

## Vector tile packs - Index ##
There are two types of Vector Tile Packs (VTPK) in **ESRI**: 
  Flat : supported by **SLYR**
  Index: not supported **SLYR**

> There is no workaround for this limitation.

> Proposed solution: waiting for funding and demand by the community to develop it.  



## Urgent fixes ##
If you have a large project impacted by limitations that requires an urgent fix, [contact us](mailto:info@north-road.com) here at **North Road** and we could look at a number of options. 

- Undertake the conversion for you. This may attract a small fee, dependent on the work, but please ask. 
- You could fund the development of the solution to go into the tool for all and become a member of our [Hall of Fame](/user_guide/hall_of_fame)

>By asking us, you are letting us know of the limitation and by delivering a solution for you, it may help develop a solution for all in the tool. 
