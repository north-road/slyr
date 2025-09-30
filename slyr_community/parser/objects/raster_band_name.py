#!/usr/bin/env python
"""
Serializable object subclass
"""

import re

from ..exceptions import UnreadableSymbolException
from ..object import Object
from ..stream import Stream


class RasterBandName(Object):
    """
    RasterBandName
    """

    @staticmethod
    def cls_id():
        return "bc25e113-168b-11d2-8d25-0000f8780535"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.band = 0
        self.dataset_name = None

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=0)

        # e.g. "landsat_4326.tif\Band_8"
        band = stream.read_string("band?")

        try:
            self.band = int(re.search(r"(\d+)$", band).group(1))
        except AttributeError as e:
            raise UnreadableSymbolException(
                "Could not read raster band number from string {}".format(band)
            ) from e

        stream.read_string("uri?")
        stream.read_string("band name?")
        stream.read_ushort("unknown", expected=1)
        self.dataset_name = stream.read_object("dataset name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "band": self.band,
            "dataset_name": self.dataset_name.to_dict() if self.dataset_name else None,
        }
