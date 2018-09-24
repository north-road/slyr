This is a work-in-progress reverse-engineered specification of ESRI .style files. This document tends to be out of date, with the best documentation of the specification being the Python parser code itself.

Specification of .style files
===
ESRI .style files are actually renamed Microsoft Access databases. Renaming the .style file to .mdb allows it to be opened directly within Access. 

The database contains a number of tables for the different style types, eg "Line Symbols", "Marker Symbols", "Color Ramps". While these tables contain fields for the symbol name, category, and tags, unfortunately the symbol itself is stored inside a binary data column. Note that earlier versions of style files (pre ArcGIS 10?) do not have the tags field in these tables.

The included `slyr/tools/style_to_bin.py` script can bulk export these symbol binary blobs from a .style file. (Note that all command line tools in slyr require mdbtools within the current path). 

We'll refer to a binary blob representing a single symbol as a "symbol section".

Relationship to .lyr files
===
While .lyr files include much more than just a layer's symbology, they do appear to utilise the same symbol section format as .style files. It may be possible to automatically detect the symbol sections within lyr files and automatically extract them, avoiding the need for the intermediate .style file.

Specification for Symbol Sections
===

Colors
---

Colors are encoded inside a symbol using the CIELAB color model. They are represented as a sequence of 3 8-byte, little endian doubles, corresponding to the L, A and B components of the color.

For instance, #ff0000 is represented as

    63 29 92 AF 04 46 4C 40
    09 17 68 51 90 39 53 40
    82 A2 B8 D4 9E 06 51 40
    
This corresponds to

- L: 56.547018
- A: 76.899433
- B: 68.103444

It seems that ESRI utilises Apple RGB Model as RGB Model with Whitepoint D65 and Gamma 1.8. Using these settings, we get RGB values very similar to those showed into ESRI products. Only for RGB values very close to zero, we have sometimes small differences, probably due to some approximation.

The conversion rules and value can be found on [Bruce Lindbloom site](http://www.brucelindbloom.com/)

Immediately following the 8-byte color components, the next byte indicates whether the color has the "use windows dithering" option enabled (!) Not sure who really cares about this option anymore, but the following values are possible for this byte:

- `00`: no dithering
- `01`: dither

The next byte indicates whether the color is a null color. A value of 00 indicates not null, and FF indicates a null (transparent) color.

Color models
---
Color models are represented by a byte, where

- `92`: HSV
- `96`: RGB
- `97`: CMYK

Internally both RGB and HSV colors are stored identically (as described above). CMYK colors seem to be stored differently, although more investigation is needed.

Symbol spec
===

Symbol Header:
--------------
The first two bytes indicate the symbol type, with known values:

- `04 E6`: Fill symbol
- `FF E5`: Marker symbol
- `FA E5`: Line symbol 

Then the following section, of unknown purpose but it's always the same in all styles encountered so far:

- `14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41`: unknown sequence (1)
- `02`: unknown meaning (B)
- `00`: probably padding
- `0D`: likely 'end of section' flag
- 7 x `00` padding

Line symbols
---

Structure of line symbol styles:

Starts with 4 byte, little endian int representing the number of levels in symbol.

The next section is repeated for each level in the symbol. Levels are in reverse z-order, ie the bottom most level comes first.

First, a 2 byte unsigned integer representing the line symbol type enum. Known values are:

- `F9 E5`: Simple line
- `FD E5`: Marker line
- `FB E5`: Cartographic line
- `FC E5`: Hash line

The following is the structure for "simple line" types:

- `14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41`: unknown sequence (1)
- `01`: unknown, but probably relates to the `02` (B) byte from the beginning of the symbol block
- `00`: padding
- color model byte (see above)
- `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01`: unknown sequence (2)
- `00` x 2 padding
- 26 bytes: L/A/B color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- 8 bytes: outline width as a little endian double
- little endian unsigned int, for line type (see below)
- `0D` byte: again, likely an "end of section" flag
- `00` x 7: padding

Line types are encoded using a single byte unsigned integer, with the following values:

- 0: Solid
- 1: Dashed
- 2: Dotted
- 3: Dash dot
- 4: Dash dot dot
- 5: Null

After this is repeated for each symbol layer, there's then two more repeating array sections. These are repeated for each symbol layer (in reverse z-order, as above).

The first consists of little endian unsigned ints, with values 1 for enabled symbol layers or 0 for disabled layers. There will be as many sequential unsigned ints here as there are symbol layers.

The second consists of little endian unsigned ints, with values 1 for locked symbol layers or 0 for unlocked layers. There will be as many sequential unsigned ints here as there are symbol layers.

Following this is a terminator of unknown meaning - `02`, then a bunch of `00` padding bytes (repeated varying times)


Fill symbols
---

Following the symbol header we have a section which follows the same format as the outline and fill (described below), but of unknown purpose. This always seems to be the same values in all generated styles:

 - `96`: RGB color model flag
 - `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01`: unknown sequence (2)
 - 3 x LAB color doubles (see above), but always black in reference files
 - `00`: likely the 'no dither' flag for some default black color
 - `00`: likely a 'not null' flag for this default black, dithered color
 - `01`: number of levels in symbol - seems to take 4 bytes, little endian
 
 - 2 byte integer: fill symbol type enum
 
Fill symbol types:

- `03 E6`: Simple fill
- `06 E6`: Line pattern fill
- `08 E6`: Marker fill
- `09 E6`: Gradient fill

The following is the structure for "simple fill" types:

A block of unknown purpose:
- `14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41`: repetion of unknown sequence (1) from above
- `01`: unknown, but probably relates to the `02` (B) byte from the beginning of the symbol block
- `00 F9 E5 14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41 01 00`: unknown sequence (3)

The interesting part of a fill symbol section follows this. While it's unknown what the bytes before this offset represent, but for the selection of simple fill styles used as reference these bytes were identical.

The next 67 bytes seem to represent the outline style:

- 1 byte: The color model (92/96/97)
- 20 bytes: `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01 00 00` repetition of unknown sequence (2)
- 26 bytes: L/A/B color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- 8 bytes: outline width as a little endian double

There's then 4 empty bytes, followed by a 0D byte. This 0D byte is likely a flag to indicate the start of the fill style. Then 7 more empty bytes.

Following this begins the fill style section:

- 1 byte: The color model.
- 20 bytes: `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01 00 00` repitition of unknown sequence (2)
- 26 bytes: L/A/B color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- `0D` byte: again, likely an "end of section" flag
- `00` x 11: padding
- little endian unsigned int, with a value 1 for enabled symbol layers or 0 for disabled layers
- little endian unsigned int, with a value 1 for locked symbol layers or 0 for unlocked layers
- `02`: unknown meaning
