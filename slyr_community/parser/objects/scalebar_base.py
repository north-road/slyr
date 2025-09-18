#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from .units import Units
from ..stream import Stream


class ScalebarBase(Object):
    """
    Scalebar base class
    """

    SCALE_BAR_NONE = 0
    SCALE_BAR_ONE = 1
    SCALE_BAR_MAJOR_DIVISIONS = 2
    SCALE_BAR_DIVISIONS = 3
    SCALE_BAR_DIVISIONS_AND_FIRST_MIDPOINT = 4
    SCALE_BAR_DIVISIONS_AND_FIRST_SUBDIVISIONS = 5
    SCALE_BAR_DIVISIONS_AND_SUBDIVISIONS = 6

    ABOVE_BAR = 0
    ALIGN_TO_TOP = 1
    CENTER_ON_BAR = 2
    ALIGN_TO_BOTTOM_OF_BAR = 3
    BELOW_BAR = 4

    RESIZE_FIXED = 0  # adjust width
    RESIZE_AUTO_DIVISION_SIZE = 1  # number of divisions
    RESIZE_AUTO_DIVISION_COUNT = 2
    RESIZE_AUTO_DIVISION_AND_DIVISION_VALUES = 3

    ABOVE_CENTER = 0
    BEFORE_LABELS = 1
    AFTER_LABELS = 2
    BEFORE_BAR = 3
    AFTER_BAR = 4
    BELOW_CENTER = 5
    ABOVE_LEFT = 6
    ABOVE_RIGHT = 7
    ABOVE_BOTH_ENDS = 8
    BEFORE_AND_AFTER_LABELS = 9
    BEFORE_AND_AFTER_BAR = 10
    BELOW_LEFT = 11
    BELOW_RIGHT = 12
    BELOW_BOTH_ENDS = 13

    @staticmethod
    def label_pos_to_string(pos) -> str:
        if pos == ScalebarBase.ABOVE_CENTER:
            return "above_center"
        elif pos == ScalebarBase.BEFORE_LABELS:
            return "before_labels"
        elif pos == ScalebarBase.AFTER_LABELS:
            return "after_labels"
        elif pos == ScalebarBase.BEFORE_BAR:
            return "before_bar"
        elif pos == ScalebarBase.AFTER_BAR:
            return "after_bar"
        elif pos == ScalebarBase.BELOW_CENTER:
            return "below_center"
        elif pos == ScalebarBase.ABOVE_LEFT:
            return "above_left"
        elif pos == ScalebarBase.ABOVE_RIGHT:
            return "above_right"
        elif pos == ScalebarBase.ABOVE_BOTH_ENDS:
            return "above_both_ends"
        elif pos == ScalebarBase.BEFORE_AND_AFTER_LABELS:
            return "before_and_after_labels"
        elif pos == ScalebarBase.BEFORE_AND_AFTER_BAR:
            return "before_and_after_bar"
        elif pos == ScalebarBase.BELOW_LEFT:
            return "below_left"
        elif pos == ScalebarBase.BELOW_RIGHT:
            return "below_right"
        elif pos == ScalebarBase.BELOW_BOTH_ENDS:
            return "below_both_ends"
        assert False, pos

    @staticmethod
    def frequency_to_string(frequency) -> str:
        if frequency == ScalebarBase.SCALE_BAR_NONE:
            return "none"
        elif frequency == ScalebarBase.SCALE_BAR_ONE:
            return "one"
        elif frequency == ScalebarBase.SCALE_BAR_MAJOR_DIVISIONS:
            return "major_divisions"
        elif frequency == ScalebarBase.SCALE_BAR_DIVISIONS:
            return "divisions"
        elif frequency == ScalebarBase.SCALE_BAR_DIVISIONS_AND_FIRST_MIDPOINT:
            return "divisions_and_first_midpoint"
        elif frequency == ScalebarBase.SCALE_BAR_DIVISIONS_AND_FIRST_SUBDIVISIONS:
            return "divisions_and_first_subdivisions"
        elif frequency == ScalebarBase.SCALE_BAR_DIVISIONS_AND_SUBDIVISIONS:
            return "divisions_and_subdivisions"
        assert False

    @staticmethod
    def position_to_string(position) -> str:
        if position == ScalebarBase.ABOVE_BAR:
            return "above_bar"
        elif position == ScalebarBase.ALIGN_TO_TOP:
            return "align_to_top"
        elif position == ScalebarBase.CENTER_ON_BAR:
            return "center_on_bar"
        elif position == ScalebarBase.ALIGN_TO_BOTTOM_OF_BAR:
            return "align_to_bottom"
        elif position == ScalebarBase.BELOW_BAR:
            return "below_bar"
        assert False

    @staticmethod
    def resize_to_string(resize) -> str:
        if resize == ScalebarBase.RESIZE_FIXED:
            return "fixed"
        elif resize == ScalebarBase.RESIZE_AUTO_DIVISION_SIZE:
            return "auto_division_value"
        elif resize == ScalebarBase.RESIZE_AUTO_DIVISION_COUNT:
            return "auto_division_count"
        elif resize == ScalebarBase.RESIZE_AUTO_DIVISION_AND_DIVISION_VALUES:
            return "auto_divisions_and_division_values"
        assert False

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.linked_map = None
        self.divisions = 5
        self.element_name = ""
        self.sub_divisions = 2
        self.text_symbol = None
        self.label_frequency = ScalebarBase.SCALE_BAR_NONE
        self.number_symbol = None
        self.bar_line_symbol = None
        self.sub_division_line_symbol = None
        self.division_line_symbol = None
        self.label_gap = 3
        self.mark_frequency = ScalebarBase.SCALE_BAR_NONE
        self.division_height = 5
        self.sub_division_height = 3
        self.mark_position = ScalebarBase.BELOW_BAR
        self.label_position = ScalebarBase.BELOW_BAR
        self.use_fraction_chars = False
        self.division_units = Units.DISTANCE_MILES
        self.division_unit_label = "Miles"
        self.division_unit_label_gap = 3
        self.division_unit_label_position = 2
        self.show_one_div_before_zero = True
        self.division_value = 100
        self.resize_strategy = ScalebarBase.RESIZE_AUTO_DIVISION_SIZE
        self.number_format = None
        self.preserve_aspect_ratio = False
        self.align_to_zero_division = False

    def _read(self, stream: Stream, version, type_string):
        internal_version = stream.read_ushort("internal version", expected=(3, 4, 6))
        internal_subversion = stream.read_ushort(
            "internal subversion", expected=(1, 2, 3)
        )
        self.element_name = stream.read_string("name")

        self.linked_map = stream.read_object("linked map")

        if not (internal_version == 3 and internal_subversion == 1):
            self.preserve_aspect_ratio = (
                stream.read_ushort("preserve aspect ratio") != 0
            )

        if internal_version > 3:
            stream.read_int("unknown", expected=1)
            stream.read_ushort("unknown", expected=0)
            stream.read_int("unknown", expected=(751861752, 32760))

            stream.read_int("unknown", expected=(0, 1718205103))
            stream.read_int("unknown", expected=(0, 417611817))
            stream.read_int("unknown", expected=(0, 3717868566))
            stream.read_int("unknown", expected=(0, 401621030))
            stream.read_int("unknown", expected=(0, 3840052040))
            stream.read_ushort("unknown", expected=(0, 16426))

        self.division_value = stream.read_double("division value")
        self.divisions = stream.read_ushort("divisions")
        self.show_one_div_before_zero = (
            stream.read_ushort("show one division before zero") != 0
        )
        self.sub_divisions = stream.read_ushort("sub_divisions")
        self.division_units = stream.read_int("division units")
        self.division_unit_label = stream.read_string("division unit label")
        self.division_unit_label_position = stream.read_int(
            "division unit label position"
        )
        self.division_unit_label_gap = stream.read_double("division unit label gap")
        self.text_symbol = stream.read_object("text symbol")
        self.label_frequency = stream.read_int("label_frequency")
        self.label_position = stream.read_int("label position")
        self.label_gap = stream.read_double("gap")
        self.number_symbol = stream.read_object("number symbol")
        self.number_format = stream.read_object("numeric format")

        if internal_version > 3:
            self.resize_strategy = stream.read_int("when resizing adjust")
            stream.read_int("unknown", expected=0)

        if internal_version > 4:
            stream.read_int("unknown", expected=0)

        self.align_to_zero_division = stream.read_ushort("align to zero division") != 0

        self.use_fraction_chars = stream.read_ushort("use fraction chars") != 0

        stream.read_ushort("unknown", expected=1)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "divisions": self.divisions,
            "sub_divisions": self.sub_divisions,
            "text_symbol": self.text_symbol.to_dict() if self.text_symbol else None,
            "label_frequency": ScalebarBase.frequency_to_string(self.label_frequency),
            "mark_frequency": ScalebarBase.frequency_to_string(self.mark_frequency),
            "number_symbol": self.number_symbol.to_dict()
            if self.number_symbol
            else None,
            "bar_line_symbol": self.bar_line_symbol.to_dict()
            if self.bar_line_symbol
            else None,
            "division_line_symbol": self.division_line_symbol.to_dict()
            if self.division_line_symbol
            else None,
            "sub_division_line_symbol": self.sub_division_line_symbol.to_dict()
            if self.sub_division_line_symbol
            else None,
            "label_gap": self.label_gap,
            "division_height": self.division_height,
            "sub_division_height": self.sub_division_height,
            "mark_position": ScalebarBase.position_to_string(self.mark_position),
            "label_position": ScalebarBase.position_to_string(self.label_position),
            "use_fraction_chars": self.use_fraction_chars,
            "division_units": Units.distance_unit_to_string(self.division_units),
            "division_unit_label": self.division_unit_label,
            "division_unit_label_gap": self.division_unit_label_gap,
            "division_unit_label_position": ScalebarBase.label_pos_to_string(
                self.division_unit_label_position
            ),
            "show_one_div_before_zero": self.show_one_div_before_zero,
            "division_value": self.division_value,
            "resize_strategy": ScalebarBase.resize_to_string(self.resize_strategy),
            "number_format": self.number_format.to_dict()
            if self.number_format
            else None,
            "linked_map": self.linked_map,
            "preserve_aspect_ratio": self.preserve_aspect_ratio,
            "element_name": self.element_name,
            "align_to_zero_division": self.align_to_zero_division,
        }
