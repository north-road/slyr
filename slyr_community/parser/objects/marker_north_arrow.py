#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class MarkerNorthArrow(Object):
    """
    MarkerNorthArrow
    """

    @staticmethod
    def cls_id():
        return "7a3f91dd-b9e3-11d1-8756-0000f8751720"

    ANGLE_DATA_FRAME = 0
    ANGLE_ABSOLUTE = 1

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.orientation_type = MarkerNorthArrow.ANGLE_ABSOLUTE
        self.name = ""
        self.linked_map = None
        self.angle = 0
        self.size = 0
        self.marker_element = None
        self.calibration_angle = 0
        self.calculated_angle = 0
        self.fixed_aspect_ratio = False
        self.reference_location = None

    @staticmethod
    def angle_to_string(angle):
        if angle == MarkerNorthArrow.ANGLE_ABSOLUTE:
            return "absolute"
        elif angle == MarkerNorthArrow.ANGLE_DATA_FRAME:
            return "data_frame"

        return None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort("internal version", expected=(2, 3, 4))

        internal_subversion = stream.read_ushort(
            "internal subversion", expected=(1, 2, 3)
        )

        self.name = stream.read_string("name")
        self.linked_map = stream.read_object("linked map")

        if not (internal_version == 3 and internal_subversion == 1):
            self.fixed_aspect_ratio = stream.read_ushort("fixed aspect ratio") != 0
        stream.read_double("angle?")

        stream.read_double("unknown", expected=(0, 28.53820000000087))
        stream.read_double("unknown", expected=(0, 28.73660000000018))
        stream.read_double("unknown", expected=(0, 31.078199999999924))
        if internal_version > 2:
            self.size = stream.read_double("size")
            if internal_subversion > 2:
                self.calculated_angle = stream.read_double("calculated angle")
                self.calibration_angle = stream.read_double("calibration angle")
                self.reference_location = stream.read_object("reference location")

                # 2/4/3 yes

                # 2/3/3 no
            if internal_version >= 4:
                self.orientation_type = stream.read_int("orientation type")
        else:
            # orientation type??
            stream.read_int("unknown", expected=0)

        self.marker_element = stream.read_object("marker element")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "orientation_type": MarkerNorthArrow.angle_to_string(self.orientation_type),
            "name": self.name,
            "linked_map": self.linked_map,
            "angle": self.angle,
            "size": self.size,
            "marker_element": self.marker_element.to_dict()
            if self.marker_element
            else None,
            "calibration_angle": self.calibration_angle,
            "calculated_angle": self.calculated_angle,
            "reference_location": self.reference_location.to_dict()
            if self.reference_location
            else None,
        }
