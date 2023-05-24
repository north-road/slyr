# pylint: disable=bad-continuation,too-many-lines

"""
Test symbol parsing
"""

import unittest
import os
import ast
import pprint
from qgis.PyQt.QtGui import QGuiApplication
from ..parser.object_registry import ObjectRegistry
from ..parser.initalize_registry import initialize_registry
from ..parser.objects.multi_layer_symbols import MultiLayerSymbol
from ..parser.exceptions import NotImplementedException
from ..parser.stream import Stream
from ..converters.context import Context
from ..converters.symbols import SymbolConverter
from .utils import Utils

expected = {
    'cmyk_bin': {
        'C 0 M 0 Y 0 B 100.bin': True,
        'C 0 M 0 Y 0 B 50.bin': True,
        'C 0 M 0 Y 100 B 0.bin': True,
        'C 0 M 0 Y 50 B 0.bin': True,
        'C 0 M 100 Y 0 B 0.bin': True,
        'C 0 M 50 Y 0 B 0.bin': True,
        'C 100 M 0 Y 0 B 0.bin': True,
        'C 15 M 24 Y 33 B 42.bin': True,
        'C 50 M 0 Y 0 B 0.bin': True
    },
    'color_symbol': {
        'color_symbol_blue_band_3.bin': True,
        'color_symbol_green_band_2.bin': True,
        'color_symbol_red_band_1.bin': True
    },
    'fill_bin': {
        '3D Texture fill R255 G0 B0.bin': True,
        'Abandoned irrigated perennial horticulture.bin': True,
        'Black CMYK.bin': True,
        'Black HSV.bin': True,
        'Black cm.bin': True,
        'Black dither non null  no outline.bin': True,
        'Black dither null.bin': True,
        'Black inches.bin': True,
        'Black mm.bin': True,
        'Black null.bin': True,
        'Black outline R0 G0 B0 disabled outline.bin': True,
        'Black outline R0 G0 B0 no color.bin': True,
        'Black outline R0 G0 B0.bin': True,
        'Black.bin': True,
        'Gradient fill Intervals 13 Percent 14 Angle 15.bin': True,
        'Gradient fill buffered.bin': True,
        'Gradient fill circular.bin': True,
        'Gradient fill rectangular.bin': True,
        'Gradient fill.bin': True,
        'Line fill angle 45 offset 3 separation 5.bin': True,
        'Line fill green outline.bin': True,
        'Line fill.bin': True,
        'Marker fill offset 3 4 separation 5 6.bin': True,
        'Marker fill random offset 3 4 separation 5 6.bin': True,
        'Marker fill.bin': True,
        'Picture Fill Circle Angle 45 Scale X 13 Y 14 Fore Red Back Blue.bin': True,
        'Picture Fill Circle Red Outline.bin': True,
        'Picture Fill Circle Swap FgBg.bin': True,
        'Picture Fill Circle X offset -37 Y offset -47 X sep 57 Y sep 67.bin': True,
        'Picture Fill Circle.bin': True,
        'Picture Fill EMF Red Transparent Color.bin': True,
        'Picture Fill EMF.bin': True,
        'Picture Fill Version 4.bin': True,
        'Picture Fill Version 7.bin': True,
        'Picture Fill Version 8 3.bin': True,
        'Picture fill.bin': False,  # This symbol is corrupt
        'R0 G0 B1 dither.bin': True,
        'R0 G0 B1.bin': True,
        'R0 G0 B255 dither.bin': True,
        'R0 G0 B255.bin': True,
        'R0 G1 B0 dither.bin': True,
        'R0 G1 B0.bin': True,
        'R0 G255 B0 dither.bin': True,
        'R0 G255 B0.bin': True,
        'R1 G0 B0 dither.bin': True,
        'R1 G0 B0.bin': True,
        'R1 G1 B1.bin': True,
        'R2 G2 B2.bin': False,  # Color tolerance results in slight difference to expected
        'R254 G254 B254.bin': True,
        'R255 G0 B0 HSV.bin': True,
        'R255 G0 B0 dither.bin': True,
        'R255 G0 B0 layer disabled.bin': True,
        'R255 G0 B0 locked.bin': True,
        'R255 G0 B0 two levels.bin': True,
        'R255 G0 B0 with cartographic line outline.bin': True,
        'R255 G0 B0.bin': True,
        'R255 G255 B255 dither.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dash.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dashdot.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dashdotdot.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dithered.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dot.bin': True,
        'R255 G255 B255 outline R0 G0 B0 null.bin': True,
        'R255 G255 B255 outline R0 G0 B0 width 2.bin': True,
        'R255 G255 B255 outline R0 G0 B0.bin': True,
        'R255 G255 B255 outline R255 G255 B255.bin': True,
        'R255 G255 B255.bin': True,
        'Simple fill with simple outline.bin': True,
        'Simple fill with two layer outline.bin': True,
        'Two layer with two layer outlines.bin': True,
        'many layers.bin': True,
        'v10_5.bin': True
    },
    'hsv_bin': {
        'H 0 S 16 V 25.bin': True,
        'H 115 S 100 V 25.bin': True,
        'H 115 S 16 V 100.bin': True,
        'H 115 S 16 V 25.bin': True,
        'H 350 S 16 V 25.bin': True,
        'H 360 S 16 V 25.bin': True
    },
    'legends_bin': {
        'Area Patch Preserve Aspect.bin': True,
        'Area Patch.bin': True,
        'Horizontal Bar Label Description.bin': True,
        'Horizontal Label Description.bin': True,
        'Line Patch Preserve Aspect.bin': True,
        'Line Patch.bin': True,
        'Nested Label Description.bin': True,
        'Normal Background green 3.4 outline.bin': True,
        'Normal Border red 3.2.bin': True,
        'Scale Text.bin': True,
        'Vertical Label Description.bin': True,
        'Area Patch Custom 2.bin': True,
        'Area Patch Custom.bin': True,
        'Area Patch Many No Preserve.bin': True,
        'Area Patch Many.bin': True,
        'Area Patch MultiPolygon.bin': True,
        'Line Patch Custom 1.bin': True,
        'Line Patch Custom 2.bin': True,
        'Line Patch Custom Many.bin': True,
        'Line Patch Custom No Preserve.bin': True,
        'Scale Line 15 divs 17 subdivs.bin': True,
        'Scale Line Division Units Decimeters.bin': True,
        'Scale Line Division Units Nautical Miles.bin': True,
        'Scale Line Label Gap 18 pt.bin': True,
        'Scale Line Label Pos Above Both Ends.bin': True,
        'Scale Line Label Pos Above Left.bin': True,
        'Scale Line Label Pos Above Right.bin': True,
        'Scale Line Label Pos Before and After Bar.bin': True,
        'Scale Line Label Pos Below Right.bin': True,
        'Scale Line Text Symbol Red.bin': True,
        'Scale Line custom label.bin': True,
        'Scale Line no show one div before zero.bin': True,
        'Scale Line when resizing adjust division value.bin': True,
        'Scale Line when resizing adjust division width 107 miles.bin': True,
        'Scale Line when resizing adjust divisions and division values.bin': True,
        'Scale Line when resizing adjust number of divisions.bin': True,
        'Stepped Scale Line Label Pos Below Bar Gap 6.bin': True,
        'Stepped Scale Line Label Pos Above Bar Gap 6.bin': True,
        'Stepped Scale Line Single Label.bin': True,
        'Stepped Scale Line Marks Division and First Subdivision.bin': True,
        'Stepped Scale Line Label Pos Align to Top of Bar Gap 6.bin': True,
        'Stepped Scale Line Marks End And Zero.bin': True,
        'Stepped Scale Line.bin': True,
        'Stepped Scale Line Marks Division and All Subdivisions.bin': True,
        'Stepped Scale Line Marks Divisions.bin': True,
        'Stepped Scale Line Label Pos Align to Bottom of Bar Gap 6.bin': True,
        'North Arrow Font Arial.bin': True,
        'Scale Text Absolute seperator.bin': True,
        'North Arrow Unicode 70.bin': True,
        'North Arrow Red.bin': True,
        'Scale Text Page Unit Point Map Unit NM.bin': True,
        'North Arrow Data Frame Rotation.bin': True,
        'Stepped Scale Line Pink Bar.bin': True,
        'North Arrow True North.bin': True,
        'Stepped Scale Line Mark Div Height 12 Subdiv height 11.bin': True,
        'Stepped Scale Line Number Symbol Red.bin': True,
        'Stepped Scale Line Marks Division and First Mid Point.bin': True,
        'Stepped Scale Line Single Mark.bin': True,
        'Stepped Scale Line Use Fraction Chars.bin': True,
        'Stepped Scale Line Mark Center on Bar.bin': True,
        'Stepped Scale Line Mark Div Red Subdiv Blue.bin': True,
        'Stepped Scale Line Mark Align to Top.bin': True,
        'Stepped Scale Line Mark Align to Bottom of Bar.bin': True,
        'Stepped Scale Line No Marks.bin': True,
        'North Arrow Calibration 37.5.bin': True,
        'Stepped Scale Line Label Pos Center On Bar Gap 6.bin': True,
        'Shadow using symbol.bin': True,
        'Stepped Scale Line Mark Below Bar.bin': True,
        'North Arrow Size 36.bin': True,
        'Scale Text Page Unit Inches Map Unit NM.bin': True,
        'Stepped Scale Line Label Divisions.bin': True,
        'Stepped Scale Line Label Divisions and All Subdivisions.bin': True,
        'Stepped Scale Line 15 divs 17 subdivs.bin': True,
        'Stepped Scale Line Label Divisions and First Mid Point.bin': True,
        'North Arrow Green Symbol.bin': True,
        'Scale Text Relative.bin': True,
        'Normal Shadow red yellow outline 7 width.bin': True,
        'Stepped Scale Line Label Ends and Zero.bin': True,
        'Scale Text Red.bin': True,
        'Scale Text Page Unit CM Map Unit NM.bin': True,
        'Scale Text Absolute.bin': True,
        'Stepped Scale LineGreen Text.bin': True,
        'Stepped Scale Line Label Divisions and First Subdivision.bin': True,
        'Stepped Scale Line Mark Above Bar.bin': True,
        'Stepped Scale Line No Labels.bin': True,
        'Nested Label No Leaders.bin': True,
        'Horizontal Bar Label Description No Show Labels.bin': True,
        'Nested No Automatic Size Text.bin': True,
        'Scale Line Label Pos Below Both Ends.bin': True,
        'Horizontal Bar No Show Heading.bin': True,
        'Nested Leader Symbol Red.bin': True,
        'Horizontal Bar Text Above 45 Below -45.bin': True,
        'Hollow Scale Bar.bin': True,
        'Single Division Scale Bar.bin': True,
        'Scale Line Label Pos Below Left.bin': True,
        'Scale Line Label Pos Before Labels.bin': True,
        'Hollow Scale Bar Green Yellow.bin': True,
        'Horizontal Bar Symbol Description Label.bin': True,
        'Scale Line Label Pos After Bar.bin': True,
        'Scale Line Label Pos Before And After Labels.bin': True,
        'Nested Horizontal Align Right.bin': True,
        'Horizontal Bar Label Override Patch Size 13 w 17 h.bin': True,
        'Horizontal Bar Show Layer Name Red Symbol.bin': True,
        'Nested Horizontal Align Center.bin': True,
        'Horizontal Bar Description Label Symbol.bin': True,
        'Horizontal Bar Label Description Symbol.bin': True,
        'Nested No Automatic Size Text Only Label Largest and Smallest Markers.bin': True,
        'Horizontal Bar Label Symbol Description.bin': True,
        'Nested Horizontal Align Left.bin': True,
        'Scale Line Label Pos Below Center.bin': True,
        'Horizontal Bar Show Layer Name.bin': True,
        'Horizontal Bar Description Symbol Label.bin': True,
        'Scale Line Label Pos Before Bar.bin': True,
        'Alternating Scale Bar bar color 1 blue color 2 yellow size 72.bin': True,
        'Scale Line Label Pos After Labels.bin': True,
        'Horizontal Bar Override Default Patch.bin': True,
        'Horizontal Bar Description Symbol Red.bin': True,
        'Nested Label Leader Overhang 17.bin': True,
        'Double Alternating Scale Bar.bin': True,
        'Horizontal Bar No Show Description.bin': True,
        'Horizontal Bar Label Symbol Red.bin': True,
        'Horizontal Bar Heading Symbol Red.bin': True,
        'Scale Line Label Pos Above Centre.bin': True,
        'Horizontal Bar Prevent Column Split.bin': True,
    },
    'line_bin': {
        '3d simple line symbol width 8.bin': True,
        '3d texture line symbol width 8.bin': True,
        'Cartographic line 3 positions flip all.bin': True,
        'Cartographic line 3 positions flip first.bin': True,
        'Cartographic line 3 positions no flip.bin': True,
        'Cartographic line 4 positions flip first.bin': True,
        'Cartographic line 5 positions flip first.bin': True,
        'Cartographic line bevel join.bin': True,
        'Cartographic line both arrow all flipped.bin': True,
        'Cartographic line both arrow not flipped.bin': True,
        'Cartographic line both arrow.bin': True,
        'Cartographic line end arrow fixed angle.bin': True,
        'Cartographic line end arrow flip all.bin': True,
        'Cartographic line end arrow flip first.bin': True,
        'Cartographic line end arrow.bin': True,
        'Cartographic line offset -4.bin': True,
        'Cartographic line offset 5.bin': True,
        'Cartographic line round join.bin': True,
        'Cartographic line round width 4 disabled.bin': True,
        'Cartographic line round width 4.bin': True,
        'Cartographic line round.bin': True,
        'Cartographic line square pattern interval 7 pattern 0.bin': True,
        'Cartographic line square pattern interval 7 pattern 00.bin': True,
        'Cartographic line square pattern interval 7 pattern 000.bin': True,
        'Cartographic line square pattern interval 7 pattern 001.bin': True,
        'Cartographic line square pattern interval 7 pattern 01.bin': True,
        'Cartographic line square pattern interval 7 pattern 010.bin': True,
        'Cartographic line square pattern interval 7 pattern 011.bin': True,
        'Cartographic line square pattern interval 7 pattern 1.bin': True,
        'Cartographic line square pattern interval 7 pattern 10.bin': True,
        'Cartographic line square pattern interval 7 pattern 100.bin': True,
        'Cartographic line square pattern interval 7 pattern 101.bin': True,
        'Cartographic line square pattern interval 7 pattern 1010.bin': True,
        'Cartographic line square pattern interval 7 pattern 101001000010.bin': True,
        'Cartographic line square pattern interval 7 pattern 11.bin': True,
        'Cartographic line square pattern interval 7 pattern 110.bin': True,
        'Cartographic line square pattern interval 7 pattern 111.bin': True,
        'Cartographic line square pattern interval 7.bin': True,
        'Cartographic line square.bin': True,
        'Cartographic line start arrow all flipped.bin': True,
        'Cartographic line start arrow complex.bin': True,
        'Cartographic line start arrow fixed angle.bin': True,
        'Cartographic line start arrow not flipped.bin': True,
        'Cartographic line start arrow.bin': True,
        'Cartographic line symbol width 8.bin': True,
        'Dash dot dot.bin': True,
        'Dash dot.bin': True,
        'Dashed.bin': True,
        'Dotted.bin': True,
        'Hash line offset -9.bin': True,
        'Hash line round cap.bin': True,
        'Hash line round join.bin': True,
        'Hash line symbol width 8 angle 45.bin': True,
        'Hash line symbol width 8.bin': True,
        'Line disabled.bin': True,
        'Line locked.bin': True,
        'Marker line complex symbol.bin': True,
        'Marker line symbol width 8 interval.bin': True,
        'Marker line symbol width 8 offset -5.bin': True,
        'Marker line symbol width 8 round join.bin': True,
        'Marker line symbol width 8.bin': True,
        'Null.bin': True,
        'Picture Line Check Red_Blue.bin': True,
        'Picture Line Check Scale X 17 Y 19.bin': True,
        'Picture Line Check Swap FgBg.bin': True,
        'Picture Line Check Width 13.bin': True,
        'Picture Line Check.bin': True,
        'Picture line symbol width 8.bin': False,  # corrupt
        'Solid 1.bin': True,
        'Solid 2.bin': True,
        'Three levels.bin': True,
        'Two levels with tags.bin': True,
        'Two levels.bin': True,
        'Marker line angle.bin': True,
        'Marker line angle 4.bin': True,
        'Marker line angle 3.bin': True,
        'Marker line angle 2.bin': True,
        'Marker line angle 5.bin': True,
    },
    'linev2_bin': {
        'lines.bin': True,
        'lines2.bin': True
    },
    'marker_bin': {
        'Arrow marker 12 width 8 offset 7 6 angle 45 red.bin': True,
        'Arrow marker.bin': True,
        'Character marker R255 G0 B0.bin': True,
        'Character marker Unicode 254.bin': True,
        'Character marker angle -35.bin': True,
        'Character marker angle 35.bin': True,
        'Character marker arial.bin': True,
        'Character marker size 16.bin': True,
        'Character marker v2.bin': True,
        'Character marker xoffset 7 yoffset 9.bin': True,
        'Character marker.bin': True,
        'Picture Marker Version 4.bin': True,
        'Picture Marker Version 5.bin': True,
        'Picture Marker Version 8.bin': True,
        'Picture marker.bin': False,  # Symbol is corrupt
        'Picture symbol brick Angle 45 Offset X 13 Y 17.bin': True,
        'Picture symbol brick Red_Blue.bin': True,
        'Picture symbol brick swap FG_BG.bin': True,
        'Picture symbol brick.bin': True,
        'R255 G0 B0 X diamond size 8.bin': True,
        'R255 G0 B0 X marker size 8.bin': True,
        'R255 G0 B0 circle marker size 12 halo size 7 fill.bin': True,
        'R255 G0 B0 circle marker size 12 halo size 7.bin': True,
        'R255 G0 B0 circle marker size 12.bin': True,
        'R255 G0 B0 circle marker size 8 with outline.bin': True,
        'R255 G0 B0 circle marker size 8 xoffset 2.bin': True,
        'R255 G0 B0 circle marker size 8 yoffset 3.bin': True,
        'R255 G0 B0 circle marker size 8.bin': True,
        'R255 G0 B0 cross marker size 8.bin': True,
        'R255 G0 B0 square marker size 8.bin': True,
        'Two layers different outline.bin': True,
        'Two layers with halo.bin': True,
        'Two layers.bin': True
    },
    'ramps_bin': {
        'Algorithmic Color Ramp CIELAB.bin': True,
        'Algorithmic Color Ramp HSV.bin': True,
        'Algorithmic Color Ramp LabLch.bin': True,
        'Algorithmic Color Ramp Red to Green.bin': True,
        'Multi-part Color Ramp.bin': True,
        'Preset Color Ramp 13 colors R_G_B.bin': True,
        'Random Val 12-100 Sat 13-99 Hue 14-360.bin': True,
        'Random Val 12-52 Sat 13-53 Hue 14-54 same everywhere.bin': True,
        'Random Val 12-52 Sat 13-53 Hue 14-54.bin': True
    },
    'text_bin': {
        'Angle 23.bin': True,
        'Balloon callout round.bin': True,
        'Balloon callout square tolerance 15 margins 6 7 8 5.bin': True,
        'Horizontal align center.bin': True,
        'Horizontal align full.bin': True,
        'Horizontal align left.bin': True,
        'Horizontal align right.bin': True,
        'Line callout accent.bin': True,
        'Line callout border.bin': True,
        'Line callout gap 4 tolerance 15 margins 5 6 7 5.bin': True,
        'Line callout leader.bin': True,
        'Line callout no leader no accent no border.bin': True,
        'Line callout style 2.bin': True,
        'Line callout style 7 curved anticlockwise.bin': True,
        'Line callout style L.bin': True,
        'Marker text background scale to fit text.bin': True,
        'Marker text background size 17.bin': True,
        'Simple line callout no auto snap.bin': True,
        'Simple line callout tolerance 17.bin': True,
        'Vertical align baseline.bin': True,
        'Vertical align bottom.bin': True,
        'Vertical align center.bin': True,
        'Vertical align top.bin': True,
        'CJK orientation.bin': True,
        'Not CJK orientation.bin': True
    },
    'labels_bin':
        {
            'Point offset left center only.bin': True,
            'Point offset 23323122.bin': True,
            'Polygon only inside.bin': True,
            'Polygon always straight.bin': True,
            'Point offset bottom right only.bin': True,
            'Point offset bottom left only.bin': True,
            'Polygon always horizontal.bin': True,
            'Point at angles 4 8 15 16.bin': True,
            'Point offset top right only.bin': True,
            'Point label at angle from field.bin': True,
            'Point offset bottom center only.bin': True,
            'Point offset top left only.bin': True,
            'Label line style.bin': True,
            'Label line style at best.bin': True,
            'Label line style at end.bin': True,
            'Label line style at start.bin': True,
            'Label line style at start 1-9 5.9 offset.bin': True,
            'Label line style offset 3.8.bin': True,
            'Polygon horizontal than straight.bin': True,
            'Point offset center right only.bin': True,
            'Point offset top center only.bin': True,
            'Point on top of point.bin': True,
            'Point offset 221.bin': True,
        },
    'maplex_points_bin':
        {
            'Label Point Centered.bin': True,
            'Label Point Best Position.bin': True,
            'Label Point Key Numbering.bin': True,
            'Label Point May Shift Label on Fixed Position.bin': True,
            'Label Point North.bin': True,
            'Label Point Northwest.bin': True,
            'Label Point Offset 4.7 Points.bin': True,
            'Label Point Offset Measure from Exact Symbol Outline.bin': True,
            'Label Point Offset Measure from Feature Geometry.bin': True,
            'Label Point Reduce Font Size Lower limit 4 pt step 0.5 lower limit width 90% step 5%.bin': True,
            'Label Point Rotate By Attribute 8.7 additional.bin': True,
            'Label Point Rotate By Attribute Align Horizontal.bin': True,
            'Label Point Rotate By Attribute Align Perpendicular.bin': True,
            'Label Point Rotate By Attribute.bin': True,
            'Label Point Rotate By Attribute Geographic.bin': True,
            'Label Point Rotate By Attribute No Keep Upright.bin': True,
            'Label Point Southwest.bin': True,
            'Label Point West.bin': True,
            'Label Reduce Duplicates 59 map units.bin': True,
            'Label Reduce Duplicates 59 mm.bin': True,
            'Label User Defined Zones.bin': True,
            'Label User Defined Zones clockwise 1-8.bin': True,
            'Strategy Order Abbrev compress stack reduce size.bin': True,
            'Label Background Label.bin': True,
            'Label Feature Weight 78.bin': True,
            'Label Fitting Stack.bin': True,
            'Label Fitting Stack Constrain Center.bin': True,
            'Label Fitting Stack Constrain Left.bin': True,
            'Label Fitting Stack Constrain Left or Right.bin': True,
            'Label Fitting Stack Constrain Right.bin': True,
            'Label Fitting Stack Max 29 Chars per Line.bin': True,
            'Label Fitting Stack Max 7 Lines.bin': True,
            'Label Fitting Stack Min 8 Chars Per Line.bin': True,
            'Label Fitting Stack Split Options.bin': True,
            'Label Margin Buffer 37%.bin': True,
            'Label Margin Buffer 37% hard constraint.bin': True,
            'Label max offset 109.bin': True,
            'Label Offset 4.7 Inches.bin': True,
            'Label Offset 4.7 Map Units.bin': True,
            'Label Offset 4.7 Millimeters.bin': True,
            'Label Place Overlapping.bin': True,
            'Label Point abbreviate word 7 dot aeiou remove first.bin': True,
            'Label Point Align Orientation Graticule Curved.bin': True,
            'Label Point Align Orientation Graticule Curved No Flip.bin': True,
            'Label Point Align Orientation Graticule Straight.bin': True,
            'Label Point Align Orientation Graticule Straight No Flip.bin': True
        },
    'maplex_lines_bin':
        {
            'Line Placement Contour.bin': True,
            'Line Placement Contour page align max angle 78 no ladders.bin': True,
            'Line Placement Contour page align max angle 78 place ladders.bin': True,
            'Line Placement Contour uphill align max angle 78 place ladders.bin': True,
            'Line Placement Regular align to graticule curved.bin': True,
            'Line Placement Regular align to graticule curved no flip.bin': True,
            'Line Placement Regular align to graticule straight align to direction of line.bin': True,
            'Line Placement Regular align to graticule straight.bin': True,
            'Line Placement Regular align to graticule straight no flip.bin': True,
            'Line Placement Regular Allow Stacked Labels to Straddle Sides.bin': True,
            'Line Placement Regular.bin': True,
            'Line Placement Regular Centered Curved.bin': True,
            'Line Placement Regular Centered Horizontal.bin': True,
            'Line Placement Regular Centered Perpendicular.bin': True,
            'Line Placement Regular Centered Straight.bin': True,
            'Line Placement Regular connect minimize span junction.bin': True,
            'Line Placement Regular connect unambiguous.bin': True,
            'Line Placement Regular Fitting Overrun stategy overrun top max 36 mm.bin': True,
            'Line Placement Regular Fitting Overrun stategy overrun top max 36 points.bin': True,
            'Line Placement Regular May Place Horizontal at Secondary Offset 23 to 25.bin': True,
            'Line Placement Regular May Place Horizontal at Secondary Offset.bin': True,
            'Line Placement Regular Measure Offset from Feature Geometry.bin': True,
            'Line Placement Regular min feature size 88 map units.bin': True,
            'Line Placement Regular min feature size 88 mm.bin': True,
            'Line Placement Regular no connect features one per feature.bin': True,
            'Line Placement Regular no connect features one per feature segment.bin': True,
            'Line Placement Regular no connect features one per part.bin': True,
            'Line Placement Regular Offset 4.7 Mm.bin': True,
            'Line Placement Regular Offset 4.7 Points.bin': True,
            'Line Placement Regular Offset at Best Position.bin': True,
            'Line Placement Regular Offset Constraint Above.bin': True,
            'Line Placement Regular Offset Constraint Below.bin': True,
            'Line Placement Regular Offset Constraint Left of Line.bin': True,
            'Line Placement Regular Offset Constraint Right of Line.bin': True,
            'Line Placement Regular Offset Curved.bin': True,
            'Line Placement Regular Offset Horizontal.bin': True,
            'Line Placement Regular Offset Perpendicular.bin': True,
            'Line Placement Regular Offset Position after end of line measure to center distance 51 percent tolerance 19.bin': True,
            'Line Placement Regular Offset Position along line from end measure to center distance 51 percent tolerance 19.bin': True,
            'Line Placement Regular Offset Position along line from start measure to center distance 51 percent tolerance 19.bin': True,
            'Line Placement Regular Offset Position before start measure to center distance 51 mm tolerance 19.bin': True,
            'Line Placement Regular Offset Position before start measure to center distance 51 mm tolerance 19 no use line direction.bin': True,
            'Line Placement Regular Offset Position before start measure to center distance 51 percent tolerance 19.bin': True,
            'Line Placement Regular Offset Position before start measure to farthest side distance 51 percent tolerance 19.bin': True,
            'Line Placement Regular Offset Position before start measure to nearest side distance 51 percent tolerance 19.bin': True,
            'Line Placement Regular Offset Straight.bin': True,
            'Line Placement Regular Repeat 47 map units.bin': True,
            'Line Placement Regular Repeat 47 mm.bin': True,
            'Line Placement Regular Repeat 47 mm prefer near label junction 27 units clearance.bin': True,
            'Line Placement Regular Repeat 47 mm prefer near map border 37 units clearance.bin': True,
            'Line Placement River.bin': True,
            'Line Placement Street Address.bin': True,
            'Line Placement Street.bin': True,
            'Line Placement Street end of street clearance min 29 preferred 33 percent.bin': True,
            'Line Placement Street may place horizontal centered on street.bin': True,
            'Line Placement Street may place primary label under when stacked.bin': True,
            'Line Placement Street reduce leading stacked labels which overrun.bin': True,
            'Line Placement Street spread chars max 37.bin': True,
            'Line Placement Street spread words max 78 percent.bin': True
        },
    'maplex_polygons_bin':
        {
            'Polygon regular horizontal place at fixed position.bin': True,
            'Polygon regular interior feature weight 119 boundary weight 229.bin': True,
            'Polygon regular internal zones 1-9.bin': True,
            'Polygon regular label buffer 38 percent.bin': True,
            'Polygon regular label buffer 38 percent hard.bin': True,
            'Polygon regular no avoid holes.bin': True,
            'Polygon regular no label largest feature part.bin': True,
            'Polygon regular no place outside.bin': True,
            'Polygon regular offset 55 mm.bin': True,
            'Polygon regular offset 55 points.bin': True,
            'Polygon regular offset 55 points max offset 137 percent.bin': True,
            'Polygon regular offset 55 points measure from feature geometry.bin': True,
            'Polygon regular offset curved.bin': True,
            'Polygon regular offset horizontal.bin': True,
            'Polygon regular remove dupes 37 map units.bin': True,
            'Polygon regular remove dupes 37 mm.bin': True,
            'Polygon regular spread chars 172 percent.bin': True,
            'Polygon regular spread words 119 percent.bin': True,
            'Polygon regular straight.bin': True,
            'Polygon regular try horizontal first.bin': True,
            'Polygon repeat 42 map units.bin': True,
            'Polygon repeat 42 mm.bin': True,
            'Polygon river placement.bin': True,
            'Polygon boundary placement allow boundary labeling of holes.bin': True,
            'Polygon boundary placement allow single sided boundary.bin': True,
            'Polygon boundary placement allow single sided boundary centered position on line.bin': True,
            'Polygon boundary placement.bin': True,
            'Polygon fitting overrun 36 mm.bin': True,
            'Polygon fitting overrun 36 points allow asymmetric.bin': True,
            'Polygon fitting overrun 36 points.bin': True,
            'Polygon land parcel placement.bin': True,
            'Polygon min area 19 map units.bin': True,
            'Polygon min area 19 mm.bin': True,
            'Polygon min length 19 map units.bin': True,
            'Polygon min length 19 mm.bin': True,
            'Polygon regular align to graticule curved.bin': True,
            'Polygon regular align to graticule curved no flip.bin': True,
            'Polygon regular align to graticule straight.bin': True,
            'Polygon regular align to graticule straight no flip.bin': True,
            'Polygon regular anchor closest point on polygon outline.bin': True,
            'Polygon regular anchor eroded center always within.bin': True,
            'Polygon regular anchor geometric center of unclipped.bin': True,
            'Polygon regular anchor geometryic center.bin': True,
            'Polygon regular.bin': True,
            'Polygon regular curved.bin': True,
            'Polygon regular external zones 1-8 clockwise.bin': True,
            'Polygon regular horizontal.bin': True
        },
    'symbols3d_bin': {
        '3d simple marker red quality highest.bin': True,
        '3d character marker display face front.bin': True,
        '3d texture fill glacier angle 45.bin': True,
        '3d texture fill glacier.bin': True,
        '3d marker symbol red normalized origin .6 .7 .8.bin': True,
        '3d marker symbol red.bin': True,
        '3d marker symbol red no display face front.bin': True,
        '3d character marker red.bin': True,
        '3d simple marker red width 17.bin': True,
        '3d texture fill glacier height 5.bin': True,
        '3d character marker unicode 34.bin': True,
        '3d simple marker red Sphere Frame.bin': True,
        '3d marker symbol.bin': True,
        '3d simple line tube green width 2.7 quality max.bin': True,
        '3d simple marker red display front face.bin': True,
        '3d simple marker red offset x 11 y 21 z 31.bin': True,
        '3d character marker no keep aspect.bin': True,
        '3d texture fill glacier width 8.bin': True,
        '3d character marker offset 7 8 9.bin': True,
        '3d simple marker red no keep aspect.bin': True,
        '3d simple marker red Cone.bin': True,
        '3d character marker not vertical orientation.bin': True,
        '3d marker symbol red rotation 23 24 25.bin': True,
        '3d simple line wall green width 2.7.bin': True,
        '3d marker symbol red no keep aspect 12 x 14 y 16 z.bin': True,
        '3d marker symbol red rotate x clockwise.bin': True,
        '3d character marker rotation 14 15 16.bin': True,
        '3d simple line tube green width 2.7 quality min.bin': True,
        '3d simple marker red Cylinder.bin': True,
        '3d simple line strip green width 2.7.bin': True,
        '3d simple marker red normalized offset dx.4 dy .6 dz .8.bin': True,
        '3d character marker width 14 x size 16 y depth 0.8z.bin': True,
        '3d simple line tube green width 2.7.bin': True,
        '3d simple marker red quality lowest.bin': True,
        '3d line texture width 2.7 brick red transparent black.bin': True,
        '3d line texture width 2.7 brick vertical alignment.bin': True,
        '3d texture fill glacier red transparent black.bin': True,
        '3d character marker normalized offset 0.2 0.3 0.4.bin': True,
        '3d simple marker red Sphere.bin': True,
        '3d marker symbol red no material draping.bin': True,
        '3d simple marker red Tetrahedron.bin': True,
        '3d simple marker red depth y 23.bin': True,
        '3d simple marker red Diamond.bin': True,
        '3d line texture width 2.7 brick.bin': True,
        '3d simple marker red Cube.bin': True,
        '3d simple marker red size z 27.bin': True,
        '3d marker symbol red offset 21 22 23.bin': True,
        '3d simple marker red rotation x13 y 16 z 19.bin': True,
        '3d marker symbol red no keep aspect.bin': True,
        '3d texture fill glacier outline blue 3.bin': True,
    },

}
initialize_registry()


class TestSymbolParser(unittest.TestCase):
    """
    Test symbol parsing
    """

    maxDiff = None

    UPDATE = False

    @staticmethod
    def read_symbol(_io_stream):
        """
        Reads a symbol from the specified file
        """
        stream = Stream(_io_stream, False, tolerant=False)
        res = stream.read_object('symbol')
        assert stream.tell() == stream.end, (stream.tell, stream.end)
        return res

    def run_symbol_checks(self, path):  # pylint: disable=too-many-locals
        """
        Checks all bin symbols against expectations
        """

        blobs = []
        for fn in os.listdir(path):
            file = os.path.join(path, fn)
            if os.path.isfile(file):
                blobs.append(file)

        for file in blobs:
            folder, symbol_name = os.path.split(file)
            path, group = os.path.split(folder)

            if symbol_name not in expected[group]:
                print("'{}': False,".format(symbol_name))

        for file in blobs:
            print(file)
            folder, symbol_name = os.path.split(file)
            path, group = os.path.split(folder)

            base, _ = os.path.splitext(symbol_name)
            expected_file = os.path.join(folder, 'expected',
                                         base + '.txt')
            expected_converted_file = os.path.join(folder, 'converted',
                                         base + '.txt')

            with open(file, 'rb') as f:
                expected_symbol = expected[group][symbol_name]
                if not expected_symbol:
                    continue

                symbol = self.read_symbol(f)
                if self.UPDATE:
                    with open(expected_file, 'w', encoding='utf8') as o:
                        pprint.pprint(symbol.to_dict(), o)
                else:
                    with open(expected_file, 'r', encoding='utf8') as o:
                        expected_res = ast.literal_eval(o.read())
                    self.assertEqual(expected_res, symbol.to_dict())

                if isinstance(symbol, MultiLayerSymbol):
                    context = Context()
                    try:
                        qgis_symbol = SymbolConverter.Symbol_to_QgsSymbol(symbol, context)
                        qgis_symbol_props = Utils.symbol_definition(qgis_symbol)
                        if self.UPDATE:
                            with open(expected_converted_file, 'wt', encoding='utf8') as o:
                                pprint.pprint(qgis_symbol_props, o)
                        else:
                            with open(expected_converted_file, 'rt', encoding='utf8') as o:
                                expected_res = o.read()
                            self.assertEqual(expected_res, qgis_symbol_props)
                    except NotImplementedException:
                        pass

    def test_lines(self):
        """
        Test line symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'line_bin')
        self.run_symbol_checks(path)

    def test_fills(self):
        """
        Test fill symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'fill_bin')
        self.run_symbol_checks(path)

    def test_markers(self):
        """
        Test marker symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'marker_bin')
        self.run_symbol_checks(path)

    def test_hsv(self):
        """
        Test HSV symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'hsv_bin')
        self.run_symbol_checks(path)

    def test_cmyk(self):
        """
        Test CMYK symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'cmyk_bin')
        self.run_symbol_checks(path)

    def test_ramps(self):
        """
        Test color ramp parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'ramps_bin')
        self.run_symbol_checks(path)

    def test_color_symbol(self):
        """
        Test color symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'color_symbol')
        self.run_symbol_checks(path)

    def test_linesv2(self):
        """
        Test simple lines v2
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'linev2_bin')
        self.run_symbol_checks(path)

    @unittest.skip('Not community')
    def test_legends(self):
        """
        Test legend type objects
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'legends_bin')
        self.run_symbol_checks(path)

    def test_text_symbols(self):
        """
        Test text symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'text_bin')
        self.run_symbol_checks(path)

    def test_label_symbols(self):
        """
        Test label symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'labels_bin')
        self.run_symbol_checks(path)

    def test_maplex_points(self):
        """
        Test label symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'maplex_points_bin')
        self.run_symbol_checks(path)

    def test_maplex_lines(self):
        """
        Test label symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'maplex_lines_bin')
        self.run_symbol_checks(path)

    def test_maplex_polygon(self):
        """
        Test label symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'maplex_polygons_bin')
        self.run_symbol_checks(path)

    def test_symbols3d(self):
        """
        Test 3d symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'symbols3d_bin')
        self.run_symbol_checks(path)

    def test_clsid_parsing(self):
        """
        Test CLSID parsing
        """
        self.assertEqual(ObjectRegistry.clsid_to_hex('7914e603-c892-11d0-8bb6-080009ee4e41'),
                         b'03e6147992c8d0118bb6080009ee4e41')
        self.assertEqual(ObjectRegistry.hex_to_clsid(b'03e6147992c8d0118bb6080009ee4e41'),
                         '7914e603-c892-11d0-8bb6-080009ee4e41')
        self.assertEqual(ObjectRegistry.hex_to_clsid(b'f5883d531a0ad211b27f0000f878229e'),
                         '533d88f5-0a1a-11d2-b27f-0000f878229e')


app = QGuiApplication([])

if __name__ == '__main__':
    unittest.main()
