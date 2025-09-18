#!/usr/bin/env python
"""
Text Symbol

Specialized text (label) properties
FULL INTERPRETATION.
"""

from ..object import Object
from ..stream import Stream


class TextSymbol(Object):
    """
    TextSymbol
    """

    CASE_NORMAL = 0
    CASE_LOWER = 1
    CASE_ALL_CAPS = 2
    CASE_SMALL_CAPS = 3

    POSITION_NORMAL = 0
    POSITION_SUPERSCRIPT = 1
    POSITION_SUBSCRIPT = 2

    HALIGN_LEFT = 0
    HALIGN_CENTER = 1
    HALIGN_RIGHT = 2
    HALIGN_FULL = 3

    VALIGN_TOP = 0
    VALIGN_CENTER = 1
    VALIGN_BASELINE = 2
    VALIGN_BOTTOM = 3

    @staticmethod
    def cls_id():
        return "b65a3e74-2993-11d1-9a43-0080c7ec5c96"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None
        self.break_character = None
        self.raster_op = 13
        self.symbol_level = 0
        self.character_spacing = 0
        self.character_width = 100
        self.word_spacing = 100
        self.flip_angle = 0.0
        self.leading = 0.0
        self.right_to_left = False
        self.kerning = True
        self.type_setting = True
        self.case = TextSymbol.CASE_NORMAL
        self.position = TextSymbol.POSITION_NORMAL
        self.x_offset = 0.0
        self.y_offset = 0.0
        self.shadow_x_offset = 0.0
        self.shadow_y_offset = 0.0
        self.shadow_color = None
        self.angle = 0.0
        self.font_size = 0
        self.font = None
        self.halo_enabled = False
        self.halo_size = 0.0
        self.halo_symbol = None
        self.background_symbol = None
        self.text_fill_symbol = None
        self.horizontal_alignment = TextSymbol.HALIGN_LEFT
        self.vertical_alignment = TextSymbol.VALIGN_TOP
        self.cjk_orientation = False
        self.text_direction = 0  # esriTextDirection
        self.clip = False
        self.rotate_with_transform = True

    @staticmethod
    def compatible_versions():
        return [1, 2, 3, 4]

    @staticmethod
    def case_to_string(case):
        """
        Converts a case enum to a string value
        """
        if case == TextSymbol.CASE_NORMAL:
            return "normal"
        elif case == TextSymbol.CASE_LOWER:
            return "lower"
        elif case == TextSymbol.CASE_ALL_CAPS:
            return "allcaps"
        elif case == TextSymbol.CASE_SMALL_CAPS:
            return "smallcaps"
        return None

    @staticmethod
    def position_to_string(position):
        """
        Converts a position enum to a string value
        """
        if position == TextSymbol.POSITION_NORMAL:
            return "normal"
        elif position == TextSymbol.POSITION_SUPERSCRIPT:
            return "superscript"
        elif position == TextSymbol.POSITION_SUBSCRIPT:
            return "subscript"
        return None

    @staticmethod
    def halign_to_string(align):
        """
        Converts horizontal alignment to a string
        """
        if align == TextSymbol.HALIGN_LEFT:
            return "left"
        elif align == TextSymbol.HALIGN_CENTER:
            return "center"
        elif align == TextSymbol.HALIGN_RIGHT:
            return "right"
        elif align == TextSymbol.HALIGN_FULL:
            return "full"
        return None

    @staticmethod
    def valign_to_string(align):
        """
        Converts vertical alignment to a string
        """
        if align == TextSymbol.VALIGN_TOP:
            return "top"
        elif align == TextSymbol.VALIGN_CENTER:
            return "center"
        elif align == TextSymbol.VALIGN_BASELINE:
            return "baseline"
        elif align == TextSymbol.VALIGN_BOTTOM:
            return "bottom"
        return None

    def read(self, stream: Stream, version):
        self.color = stream.read_object("color")
        self.break_character = stream.read_int("break character")
        if self.break_character == 0xFFFFFFFF:
            self.break_character = None

        self.vertical_alignment = stream.read_int("vertical align")
        self.horizontal_alignment = stream.read_int("horizontal align")

        self.clip = stream.read_uchar("clip") != 0
        self.right_to_left = stream.read_uchar("right to left") != 0

        self.angle = stream.read_double("angle")
        self.x_offset = stream.read_double("x_offset")
        self.y_offset = stream.read_double("y_offset")
        self.raster_op = stream.read_int("raster op")
        self.symbol_level = stream.read_int("symbol level")
        self.shadow_color = stream.read_object("shadow color")
        self.shadow_x_offset = stream.read_double("shadow x offset")
        self.shadow_y_offset = stream.read_double("shadow y offset")
        self.position = stream.read_int("position")
        self.case = stream.read_int("case")
        self.character_spacing = stream.read_double("character spacing")
        self.character_width = stream.read_double("character width")
        self.word_spacing = stream.read_double("word spacing")
        self.kerning = stream.read_uchar("kerning") == 1
        self.leading = stream.read_double("leading")
        self.text_direction = stream.read_int("text direction")
        self.flip_angle = stream.read_double("flip_angle")
        self.type_setting = stream.read_uchar("type setting") != 0

        stream.read_clsid("text path")

        self.background_symbol = stream.read_object("background symbol")
        self.text_fill_symbol = stream.read_object("text fill symbol")
        stream.read_string(
            "first sample text"
        )  # contains a sample label text, based on the expression
        self.font_size = stream.read_double("font size")

        self.halo_enabled = stream.read_int("halo enabled") != 0
        self.halo_size = stream.read_double("halo size")
        self.halo_symbol = stream.read_object("halo symbol")

        self.font = stream.read_object("font")

        if version > 1:
            self.rotate_with_transform = (
                stream.read_ushort("rotate with transform") != 0
            )

        if version > 2:
            stream.read_clsid("parser")

        if version > 3:
            self.cjk_orientation = stream.read_ushort("CJK orientation") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "color": self.color.to_dict() if self.color else None,
            "raster_op": self.raster_op,
            "symbol_level": self.symbol_level,
            "character_spacing": self.character_spacing,
            "character_width": self.character_width,
            "word_spacing": self.word_spacing,
            "flip_angle": self.flip_angle,
            "leading": self.leading,
            "right_to_left": self.right_to_left,
            "cjk_orientation": self.cjk_orientation,
            "kerning": self.kerning,
            "case": TextSymbol.case_to_string(self.case),
            "x_offset": self.x_offset,
            "y_offset": self.y_offset,
            "position": TextSymbol.position_to_string(self.position),
            "shadow_x_offset": self.shadow_x_offset,
            "shadow_y_offset": self.shadow_y_offset,
            "shadow_color": self.shadow_color.to_dict() if self.shadow_color else None,
            "angle": self.angle,
            "font_size": self.font_size,
            "font": self.font.to_dict() if self.font else None,
            "halo_enabled": self.halo_enabled,
            "halo_size": self.halo_size,
            "halo_symbol": self.halo_symbol.to_dict() if self.halo_symbol else None,
            "background_symbol": self.background_symbol.to_dict()
            if self.background_symbol
            else None,
            "horizontal_alignment": TextSymbol.halign_to_string(
                self.horizontal_alignment
            ),
            "vertical_alignment": TextSymbol.valign_to_string(self.vertical_alignment),
            "text_fill_symbol": self.text_fill_symbol.to_dict()
            if self.text_fill_symbol
            else None,
            "text_direction": self.text_direction,
            "type_setting": self.type_setting,
            "break_character": self.break_character,
            "clip": self.clip,
            "rotate_with_transform": self.rotate_with_transform,
        }
