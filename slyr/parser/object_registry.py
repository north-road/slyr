#!/usr/bin/env python
"""
A registry for all known objects which can be decoded from a Stream
"""

from slyr.parser.object import Object
from slyr.parser.exceptions import (NotImplementedException,
                                    UnknownGuidException)


class ObjectRegistry:
    """
    A registry for all known objects which can be decoded from a Stream.
    """

    NOT_IMPLEMENTED_GUIDS = {
        '9a1eba10-cdf9-11d3-81eb-0080c79f0371': 'DotDensityFillSymbol',
        '7914e609-c892-11d0-8bb6-080009ee4e41': 'GradientFillSymbol',
        '7914e5fc-c892-11d0-8bb6-080009ee4e41': 'HashLineSymbol',
        '7914e606-c892-11d0-8bb6-080009ee4e41': 'LineFillSymbol',
        '7914e608-c892-11d0-8bb6-080009ee4e41': 'MarkerFillSymbol',
        'd842b082-330c-11d2-9168-0000f87808ee': 'PictureFillSymbol',
        '22c8c5a1-84fc-11d4-834d-0080c79f0371': 'PictureLineSymbol',
        '7914e602-c892-11d0-8bb6-080009ee4e41': 'PictureMarkerSymbol',
        'b65a3e74-2993-11d1-9a43-0080c7ec5c96': 'TextSymbol',
        '5031736a-bd70-11d3-9f79-00c04f6bc709': 'BarChartSymbol',
        '6e8ec8f7-e90a-11d5-a129-00508bd60cb9': 'CharacterMarker3DSymbol',
        '773f7274-aefb-11d5-8112-00c04fa0adf8': 'Marker3DSymbol',
        '470b7275-3552-11d6-a12d-00508bd60cb9': 'SimpleLine3DSymbol',
        '773f7270-aefb-11d5-8112-00c04fa0adf8': 'SimpleMarker3DSymbol',
        '8d738780-c069-42e0-9dfa-2b7b61707ba9': 'TextureFillSymbol',
        'b5710c9c-a9bc-4a16-b578-54be176ed57b': 'TextureLineSymbol',
        '40987040-204c-11d3-a3f2-0004ac1b1d86': 'ColorRampSymbol',
        '50317368-bd70-11d3-9f79-00c04f6bc709': 'PieChartSymbol',
        '99dccb66-2e09-11d3-a626-0008c7bf3347': 'RasterRGBSymbol',
        '50317369-bd70-11d3-9f79-00c04f6bc709': 'StackedChartSymbol',
        '2b74125d-5c1b-4dbd-967a-7412dfff1f09': 'TextMarkerSymbol',
        'beb8709b-c0b4-11d0-8379-080009b996cc': 'AlgorithmicColorRamp',
    }

    def __init__(self):
        self.objects = {}

    def register(self, object_class: Object):
        """
        Registers a new object class to the registry.
        """
        self.objects[object_class.guid()] = object_class

    def create_object(self, guid: str):
        """
        Creates a new object of the type associated with guid
        """
        if guid == '00000000-0000-0000-0000-000000000000':
            return None
        if guid in self.NOT_IMPLEMENTED_GUIDS:
            raise NotImplementedException('{} objects are not yet supported'.format(self.NOT_IMPLEMENTED_GUIDS[guid]))
        elif guid not in self.objects:
            raise UnknownGuidException('Unknown GUID: {}'.format(guid))
        return self.objects[guid]()

    @staticmethod
    def guid_to_hex(guid: str):
        """
        Converts a string GUID to the binary equivalent stored in a block
        E.g.
        '7914e603-c892-11d0-8bb6-080009ee4e41' to
        03e6147992c8d0118bb6080009ee4e41
        """

        # Note: this is correct - confirmed by checking against WINE source
        # https://github.com/wine-mirror/wine/blob/6d801377055911d914226a3c6af8d8637a63fa13/dlls/compobj.dll16/compobj.c#L380

        g = guid.replace('-', '')
        res = b''
        res += g[6:8].encode()
        res += g[4:6].encode()
        res += g[2:4].encode()
        res += g[0:2].encode()
        res += g[10:12].encode()
        res += g[8:10].encode()
        res += g[14:16].encode()
        res += g[12:14].encode()
        res += g[16:].encode()
        return res

    @staticmethod
    def hex_to_guid(hex_value) -> str:
        """
        Converts a binary value to a GUID
        eg 03e6147992c8d0118bb6080009ee4e41
        to 7914e603-c892-11d0-8bb6-080009ee4e41
        """
        res = ''
        res += hex_value[6:8].decode()
        res += hex_value[4:6].decode()
        res += hex_value[2:4].decode()
        res += hex_value[0:2].decode()
        res += '-'
        res += hex_value[10:12].decode()
        res += hex_value[8:10].decode()
        res += '-'
        res += hex_value[14:16].decode()
        res += hex_value[12:14].decode()
        res += '-'
        res += hex_value[16:20].decode()
        res += '-'
        res += hex_value[20:].decode()
        return res


REGISTRY = ObjectRegistry()
