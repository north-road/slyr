from slyr.parser.object import Object
from slyr.parser.exceptions import (NotImplementedException,
                                    UnknownGuidException)


class ObjectRegistry:
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
            raise NotImplementedException('{} are not implemented yet'.format(self.NOT_IMPLEMENTED_GUIDS[guid]))
        elif guid not in self.objects:
            raise UnknownGuidException('Unknown GUID: {}'.format(guid))
        return self.objects[guid]()

    @staticmethod
    def guid_to_hex(guid: str):
        # I don't understand the reason why, but GUIDs are stored in a strange format
        # in the blobs. E.g. a GUID of
        # 7914e603-c892-11d0-8bb6-080009ee4e41
        # is stored as
        # 03e6147992c8d0118bb6080009ee4e41
        # This function converts GUIDs to the blob format

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
