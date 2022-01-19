#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..exceptions import RequiresLicenseException
from ..stream import Stream


class BaseMapLayer(Object):
    """
    BaseMapLayer
    """

    @staticmethod
    def cls_id():
        return 'da4122bf-7b07-4158-88b0-19d342bed8ba'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [11]

    def read(self, stream: Stream, version):
        raise RequiresLicenseException('Converting base map layers requires the licensed version of SLYR')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
