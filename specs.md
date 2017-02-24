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

- C: 56.547018
- I: 76.899433
- E: 68.103444

Unfortunately conversion of these values back to RGB results in R: 255, G: 43, B: 6.
At least, according to http://colormine.org/convert/rgb-to-lab we should expect:

- C: 53.23288178584245
- I: 80.10930952982204
- E: 67.22006831026425

For #ff0000. It's possible that ESRI utilise a different whitepoint in their conversion of CIELAB -> RGB. 

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

Fill symbols
---

Constant sections (in all reference files):

 - `04`: unknown meaning (A)
 - `E6 14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41`: unknown sequence (1)
 - `02`: unknown meaning (B)
 - `00`: probably padding
 - `0D`: likely 'end of section' flag
 - 7 x `00` padding
 
Following this we have a section which follows the same format as the outline and fill (described below), but of unknown purpose. This always seems to be the same values in all generated styles:

 - `96`: RGB color model flag
 - `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01`: unknown sequence (2)
 - `00 00`: padding?
 - 3 x CIE color doubles (see above), but always black in reference files
 - `01`: likely the 'dither' flag for some default black color
 - `00`: likely a 'not null' flag for this default black, dithered color
 - `00 00`: padding?
 
Then another block of unknown purpose:

- `03`: unknown, but I suspect it relates to the `04` (A) byte which begins the symbol block
- `E6 14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41`: repetion of unknown sequence (1) from above
- `01`: unknown, but probably relates to the `02` (B) byte from the beginning of the symbol block
- `00 F9 E5 14 79 92 C8 D0 11 8B B6 08 00 09 EE 4E 41 01 00`: unknown sequence (3)

The interesting part of a fill symbol section follows this. While it's unknown what the bytes before this offset represent, but for the selection of simple fill styles used as reference these bytes were identical.

The next 67 bytes seem to represent the outline style:

- 1 byte: The color model (92/96/97)
- 20 bytes: `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01 00 00` repetition of unknown sequence (2)
- 26 bytes: C/I/E color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- 8 bytes: outline width as a little endian double

There's then 4 empty bytes, followed by a 0D byte. This 0D byte is likely a flag to indicate the start of the fill style. Then 7 more empty bytes.

Following this begins the fill style section:

- 1 byte: The color model.
- 20 bytes: `C4 E9 7E 23 D1 D0 11 83 83 08 00 09 B9 96 CC 01 00 01 00 00` repitition of unknown sequence (2)
- 26 bytes: C/I/E color components as 3 8-byte doubles + 2 bytes for the dithered/null flags (as described above) 
- `0D` byte: again, likely an "end of section" flag
- '00' x 11: padding
- '01' for enabled symbol layers, '00' for disabled layers

