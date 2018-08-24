![SLYR Logo](logo.png)

# SLYR

A Python library and set of command line tools for extraction, parsing, and conversion of ESRI `.lyr` and `.style` files.

[![Build Status](https://travis-ci.org/nyalldawson/esri_style_specs.svg?branch=master)](https://travis-ci.org/nyalldawson/esri_style_specs)

Status
=====

- RGB colors can be parsed, within a maximum of 1 unit difference in either the R/G/B components.
- Fill symbols
    - complete support for Simple Fill layers
- Line symbols
    - complete support for Simple Line layers
    - near complete support for Cartographic Line layers, including custom dash patterns. Arrows cannot be decoded yet.
- Marker symbols
    - complete support for Simple Marker layers
    - complete support for Character Marker layers

Tools
=====

 - `bin_dump.py` Converts a binary `.style` database row blob into a symbol and dumps the symbol properties to the console
 - `style_dump.py` Dumps the complete contents of an ESRI `.style` database, printing symbol properties to the console
 - `style_to_bin.py` Exports the contents of an ESRI `.style` database to individual `.bin` binary files, each containing an encoded version of a single symbol
 - `style_to_qgis_xml.py` Converts the contents of an ESRI `.style` database to a QGIS 3.x Style `.xml` file, ready for importing direct into your QGIS style library (requires QGIS 3.x)
 
 All tools require the command line `mdbtools` for handling the `.style` database files. Binaries of these can be downloaded from [https://github.com/lsgunth/mdbtools-win](https://github.com/lsgunth/mdbtools-win), and they should be extracted and available in the Windows path.
 
Specifications
==============

Some description of the `.style` binary format can be found in [specs.md](specs.md), although the most up-to-date reference is the Python parsing code itself.