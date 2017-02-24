This is a work-in-progress reverse-engineered specification of ESRI .style files

Specification of .style files
===
ESRI .style files are actually renamed Microsoft Access databases. Renaming the .style file to .mdb allows it to be opened directly within Access. 

The database contains a number of tables for the different style types, eg "Line Symbols", "Marker Symbols", "Color Ramps". While these tables contain fields for the symbol name, category, and tags, unfortunately the symbol itself is stored inside a binary data column.

We'll refer to a binary blob representing a single symbol as a "symbol section".

Relationship to .lyr files
===
While .lyr files include much more than just a layer's symbology, they do appear to utilise the same symbol section format as .style files. It may be possible to automatically detect the symbol sections within lyr files and automatically extract them, avoiding the need for the intermediate .style file.

Specification for Symbol Sections
===

Colors
---

Colors are encoded inside a symbol using the CIELAB color model. They are represented as a sequence of 3 8-byte, little endian doubles, corresponding to the C, I and E components of the color.

For instance, #ff0000 is represented as

    63 29 92 AF 04 46 4C 40
    09 17 68 51 90 39 53 40
    82 A2 B8 D4 9E 06 51 40
    
This corresponds to
C: 56.547018
I: 76.899433
E: 68.103444

Unfortunately conversion of these values back to RGB results in R: 255, G: 43, B: 6.
At least, according to http://colormine.org/convert/rgb-to-lab we should expect:
C: 53.23288178584245
I: 80.10930952982204
E: 67.22006831026425

For #ff0000. It's possible that ESRI utilise a different whitepoint in their conversion of CIELAB -> RGB. 

Immediately following the 8-byte color components, the next byte indicates whether the color has the "use windows dithering" option enabled (!) Not sure who really cares about this option anymore, but the following values are possible for this byte:

00: no dithering
01: dither

The next byte indicates whether the color is a null color. A value of 00 indicates not null, and FF indicates a null (transparent) color.

Color models
---
Color models are represented by a byte, where
96: RGB
92: HSV
97: CMYK

Internally both RGB and HSV colors are stored identically (as described above). CMYK colors seem to be stored differently, although more investigation is needed.

Fill symbols
---

In the reference files included in this repo, the interesting part of a fill symbol section starts at offset 0x71. It's unknown what the bytes before this offset represent, but for the selection of simple fill styles used as reference these bytes were identical.

The 67 bytes from 0x71 seem to represent the outline style:

- 1 byte: The color model.
- 20 bytes: unknown
- 26 bytes: C/I/E color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- 8 bytes: outline width as a little endian double

There's then 4 empty bytes, followed by a 0D byte. This 0D byte is likely a flag to indicate the start of the fill style. Then 7 more empty bytes.

Following this begins the fill style section:

- 1 byte: The color model.
- 20 bytes: unknown
- 26 bytes: C/I/E color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- '0D' byte: again, likely an "end of section" flag

