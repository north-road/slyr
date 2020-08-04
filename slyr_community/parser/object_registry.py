#!/usr/bin/env python
"""
A registry for all known objects which can be decoded from a Stream
"""

from slyr_community.parser.exceptions import UnknownClsidException, CustomExtensionClsidException


class ObjectRegistry:
    """
    A registry for all known objects which can be decoded from a Stream.
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        self.objects = {}
        self.classes = []

    def register(self, object_class):
        """
        Registers a new object class to the registry.
        """
        cls_id = object_class.cls_id()

        if not cls_id:
            return
        else:
            cls_id = tuple([int(c, base=16) for c in cls_id.split('-')])
            self.classes.append(object_class)

        # assert cls_id not in self.objects, (object_class, self.objects[cls_id])
        self.objects[cls_id] = object_class

    def reload_clsids(self):
        """
        Reloads all known classes, regenerating clsids
        """
        self.objects = {}
        prev_classes = self.classes
        self.classes = []
        for c in prev_classes:
            self.register(c)

    def create_object(self, clsid: str):
        """
        Creates a new object of the type associated with clsid
        """
        if clsid == (0, 0, 0, 0, 0):
            return None

        if clsid in self.objects:
            return self.objects[clsid]()
        elif clsid in CUSTOM_EXTENSION_CLSIDS:
            raise CustomExtensionClsidException('Custom extension: {}-{}-{}-{}-{}'.format(*[hex(c)[2:] for c in clsid]),
                                                clsid='{}-{}-{}-{}-{}'.format(*[hex(c)[2:] for c in clsid]))
        raise UnknownClsidException('Unknown CLSID: {}-{}-{}-{}-{}'.format(*[hex(c)[2:] for c in clsid]))

    @staticmethod
    def clsid_to_hex(clsid: str):
        """
        Converts a string CLSID to the binary equivalent stored in a block
        E.g.
        '7914e603-c892-11d0-8bb6-080009ee4e41' to
        03e6147992c8d0118bb6080009ee4e41
        """

        # Note: this is correct - confirmed by checking against WINE source
        # https://github.com/wine-mirror/wine/blob/6d801377055911d914226a3c6af8d8637a63fa13/dlls/compobj.dll16/compobj.c#L380

        g = clsid.replace('-', '')
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
    def hex_to_clsid(hex_value) -> str:
        """
        Converts a binary value to a CLSID
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

    @staticmethod
    def hex_to_clsid2(hex_value) -> list:
        res = (int(hex_value[6:8].decode(), base=16) * 0x1000000 +
               int(hex_value[4:6].decode(), base=16) * 0x10000 +
               int(hex_value[2:4].decode(), base=16) * 0x100 +
               int(hex_value[0:2].decode(), base=16),
               int(hex_value[10:12].decode(), base=16) * 0x100 +
               int(hex_value[8:10].decode(), base=16),
               int(hex_value[14:16].decode(), base=16) * 0x100 +
               int(hex_value[12:14].decode(), base=16),
               int(hex_value[16:20].decode(), base=16),
               int(hex_value[20:].decode(), base=16))
        return res


REGISTRY = ObjectRegistry()

CUSTOM_EXTENSION_CLSIDS = [
]
