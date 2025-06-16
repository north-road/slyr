# SLYR (community edition)

![SLYR Logo](logo.png)

A QGIS plugin for extraction, parsing, and conversion of ESRI `.lyr`, `.mxd` and `.style` files.

**This repo contains the community, open-source version of SLYR, which lags in features and capabilities from the full SLYR version. Read more about the full version and how you can obtain it on [the North Road site](https://north-road.com/slyr/).**

[![Build Status](https://travis-ci.org/nyalldawson/slyr.svg?branch=master)](https://travis-ci.org/nyalldawson/slyr)

## Status

- This open-source version only supports ESRI .style database files, and **vector** .lyr files. See [the North Road site](https://north-road.com/slyr/) for the version which supports direct MXD file conversion, and support for raster, TIN and point cloud LYR files, and the ArcGIS Pro stylx/lyrx file types.
- Full support for converting vector layers, including all symbology, labeling, all renderer types (unique, class breaks, bivariate, etc) and other general layer properties like scale ranges, hotlinks, and much much more.
- Near 100% pixel perfect support for converting all fill types, line types and marker symbol types (depending on QGIS version -- for best results always use the lastest QGIS version)
- RGB colors can be parsed, within a maximum of 1 unit difference in either the R/G/B components.
- 100% color match for other color types, including HSV, CMYK, Grayscale, etc
- All color ramp types can be parsed

## Tools

- `bin_dump.py` Converts a binary `.style` database row blob into a symbol and dumps the symbol properties to the console
- `style_dump.py` Dumps the complete contents of an ESRI `.style` database, printing symbol properties to the console
- `style_to_bin.py` Exports the contents of an ESRI `.style` database to individual `.bin` binary files, each containing an encoded version of a single symbol
- `style_to_qgis_xml.py` Converts the contents of an ESRI `.style` database to a QGIS 3.x Style `.xml` file, ready for importing direct into your QGIS style library (requires QGIS 3.x)

Style parsing tools require the command line `mdbtools` for handling the `.style` database files. Binaries of these can be downloaded from [https://github.com/lsgunth/mdbtools-win](https://github.com/lsgunth/mdbtools-win), and they should be extracted and available in the Windows path. Alternatively, you can extract them to any folder and then setup the correct path to that folder through the Settings -> Options -> SLYR panel.

LYR parsing tools do not require any additional dependencies.

## QGIS Plugin

SLYR also functions as a QGIS plugin (for QGIS >= 3.4). The community (unlicensed) version of the plugin is available via the standard QGIS plugins repository, so you can install it directly from within QGIS itself.

The plugin adds a new group to the Processing Toolbox for "SLYR", containing tools for conversion of style databases to QGIS symbol styles. Note that Windows users will first need to setup the path to the mdbtools binaries via Options - Processing - Providers - SLYR. There's also an algorithm for converting color palettes stored in style files to the standard GPL color palette text format.

The plugin throws warnings (and optionally creates a report) containing properties which cannot be translated to QGIS symbology. If you get these warnings, PLEASE consider sponsoring the feature development within QGIS itself! Everyone benefits, and you'll usually be pleasantly suprised at how inexpensive this can be! Just shoot us an email to info@north-road.com to discuss.
 
## Specifications

The most up-to-date reference is the Python parsing code itself. Read the source!

## Hall of Fame

SLYR wouldn't be possible without direct financial support for its development. The following organisations have directly contributed to SLYR development, and are deserving of gratitude!

- SMEC/SJ
- [North Road](http://north-road.com)
- [OpenGIS.ch](http://opengis.ch)

And hey, if you want to see slyr improved, why not consider financially supporting its development? Drop us a line at [info@north-road.com](mailto:info@north-road.com) to discuss.
