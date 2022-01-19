#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..exceptions import RequiresLicenseException
from ..object import Object, partially_implemented
from ..stream import Stream


class ImageServerLayer(Object):
    """
    ImageServerLayer
    """

    @staticmethod
    def cls_id():
        return '477d13e7-8d68-45b6-a7fd-2ef442bcce95'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting image server layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }


class UnknownImageServerExtension1(Object):
    """
    UnknownImageServerExtension1
    """

    @staticmethod
    def cls_id():
        return '10e996a7-f3f0-48dd-b0e4-c8920bc8c5c8'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting image server layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }


@partially_implemented
class UnknownImageServerExtension2(Object):
    """
    UnknownImageServerExtension2
    """

    @staticmethod
    def cls_id():
        return '58583803-fc0b-481d-8fea-cd516ca48fd2'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting image server layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
