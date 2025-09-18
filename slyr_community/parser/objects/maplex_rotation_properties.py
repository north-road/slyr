#!/usr/bin/env python
"""
Serializable object subclass

"""

from ..object import Object
from ..stream import Stream


class MaplexRotationProperties(Object):
    """
    MaplexRotationProperties
    """

    ROTATE_LABEL_GEOGRAPHIC = 0
    ROTATE_LABEL_ARITHMETIC = 1
    ROTATE_LABEL_RADIANS = 2
    ROTATE_LABEL_AV3 = 3

    @staticmethod
    def cls_id():
        return "20664808-bba1-ccd2-8967-f453c9ed732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.rotate_by_attribute = False
        self.rotation_type = MaplexRotationProperties.ROTATE_LABEL_GEOGRAPHIC
        self.keep_upright = True
        self.perpendicular_to_angle = False
        self.rotation_attribute = ""

    @staticmethod
    def compatible_versions():
        return [2]

    @staticmethod
    def rotate_type_to_string(rotate_type):
        """
        Converts rotation type to string
        """
        if rotate_type == MaplexRotationProperties.ROTATE_LABEL_GEOGRAPHIC:
            return "geographic"
        elif rotate_type == MaplexRotationProperties.ROTATE_LABEL_ARITHMETIC:
            return "arithmetic"
        elif rotate_type == MaplexRotationProperties.ROTATE_LABEL_RADIANS:
            return "radians"
        elif rotate_type == MaplexRotationProperties.ROTATE_LABEL_AV3:
            return "av3"
        return None

    def read(self, stream: Stream, version):
        self.rotate_by_attribute = stream.read_ushort("rotate by attribute") != 0
        self.rotation_type = stream.read_int("rotation type")
        self.rotation_attribute = stream.read_string("attribute")
        self.perpendicular_to_angle = stream.read_ushort("perpendicular to angle") != 0
        self.keep_upright = stream.read_ushort("keep upright") == 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "rotate_by_attribute": self.rotate_by_attribute,
            "rotation_attribute": self.rotation_attribute,
            "keep_upright": self.keep_upright,
            "perpendicular_to_angle": self.perpendicular_to_angle,
            "rotation_type": MaplexRotationProperties.rotate_type_to_string(
                self.rotation_type
            ),
        }
