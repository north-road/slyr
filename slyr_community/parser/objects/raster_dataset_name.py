#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RasterDatasetName2(Object):
    """
    RasterDatasetName2 -- seems like an older variant
    """

    @staticmethod
    def cls_id():
        return '76360e01-ec46-11d1-8d21-0000f8780535'
    
    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.file_name = ''
        self.path = ''
        self.type = ''
        self.workspace_name = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        self.file_name = stream.read_string('file name')
        self.path = stream.read_string('path?')
        self.type = stream.read_string('type')
        stream.read_string('unknown', expected='')
        self.workspace_name = stream.read_object('workspace name')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'file_name': self.file_name,
            'path': self.path,
            'type': self.type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }


class RasterDatasetName(Object):
    """
    RasterDatasetName
    """

    @staticmethod
    def cls_id():
        return '75bce6e2-8af5-478e-8892-fa45ca50af4d'
    
    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.file_name = ''
        self.path = ''
        self.type = ''
        self.workspace_name = None

    @staticmethod
    def compatible_versions():
        return [2, 3, 4]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        self.file_name = stream.read_string('file name')
        self.path = stream.read_string('path?')
        self.type = stream.read_string('type')
        stream.read_string('unknown', expected='')
        self.workspace_name = stream.read_object('workspace name')

        # bit of guesswork here
        if version > 2:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)
        if version > 3:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'file_name': self.file_name,
            'path': self.path,
            'type': self.type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }


class FgdbRasterDatasetName(Object):
    """
    FgdbRasterDatasetName
    """

    @staticmethod
    def cls_id():
        return 'f2137c6f-9075-4baf-9b38-e2f36083fbf4'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.file_name = ''
        self.path = ''
        self.type = ''
        self.workspace_name = None

    @staticmethod
    def compatible_versions():
        return [3, 4]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        self.file_name = stream.read_string('file name')
        self.path = stream.read_string('path?')
        if version > 3:
            self.type = stream.read_string('type', expected='Fgdb Raster Dataset')
        else:
            stream.read_string('unknown')
        stream.read_string('unknown', expected='')
        self.workspace_name = stream.read_object('workspace name')

        stream.read_ushort('unknown flag', expected=65535)
        stream.read_ushort('unknown flag', expected=65535)
        if version > 3:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)

        def handler(ref, size):
            if ref == 1:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 2:
                stream.read_string('unknown', size=size)
            elif ref == 3:
                stream.read_string('unknown', size=size)
            elif ref == 4:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 5:
                stream.read_string('unknown', size=size)
            elif ref == 6:
                assert size == 0xffffffff
                stream.read_object('unknown', allow_reference=False)
            elif ref == 7:
                assert size == 4
                stream.read_int('unknown', expected=1)
            else:
                assert False, 'Unknown property ref {}'.format(ref)

        stream.read_indexed_properties(handler)

        stream.read_ushort('unknown', expected=65535)
        stream.read_ushort('unknown', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'file_name': self.file_name,
            'path': self.path,
            'type': self.type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }


class SdeRasterDatasetName(Object):
    """
    SdeRasterDatasetName
    """

    @staticmethod
    def cls_id():
        return 'd6c003c5-a050-438e-bbd4-97294c3fddc1'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.file_name = ''
        self.path = ''
        self.type = ''
        self.workspace_name = None

    @staticmethod
    def compatible_versions():
        return [2, 3, 4]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        self.file_name = stream.read_string('file name')
        self.path = stream.read_string('path?')
        self.type = stream.read_string('type', expected='SDE Raster Dataset')
        stream.read_string('unknown', expected='')
        self.workspace_name = stream.read_object('workspace name')

        if version > 2:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)

        def handler(ref, size):
            if ref == 1:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 2:
                stream.read_string('unknown', size=size)
            elif ref == 3:
                stream.read_string('unknown', size=size)
            elif ref == 4:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 5:
                stream.read_string('unknown', size=size)
            elif ref == 6:
                assert size == 0xffffffff
                stream.read_object('unknown', allow_reference=False)
            elif ref == 7:
                assert size == 4
                stream.read_int('unknown', expected=1)
            else:
                assert False, 'Unknown property ref {}'.format(ref)

        if version > 3:
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)

        stream.read_indexed_properties(handler)

        stream.read_ushort('unknown', expected=65535)
        stream.read_ushort('unknown', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'file_name': self.file_name,
            'path': self.path,
            'type': self.type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }


class AccessRasterDatasetName(Object):
    """
    AccessRasterDatasetName
    """

    @staticmethod
    def cls_id():
        return 'c8f9dc31-d221-4635-923e-1a55a525b1a1'

    def __init__(self):
        super().__init__()
        self.name = ''
        self.dataset_name = ''

    @staticmethod
    def compatible_versions():
        return [2, 3, 4]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        self.file_name = stream.read_string('file name')
        self.path = stream.read_string('path?')
        self.type = stream.read_string('type')
        stream.read_string('unknown', expected='')
        self.workspace_name = stream.read_object('workspace name')

        if version > 2:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)
        if version > 3:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)

        def handler(ref, size):
            if ref == 1:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 2:
                stream.read_string('unknown', size=size)
            elif ref == 3:
                stream.read_string('unknown', size=size)
            elif ref == 4:
                assert size == 4
                stream.read_int('unknown', expected=1)
            elif ref == 5:
                stream.read_string('unknown', size=size)
            elif ref == 6:
                assert size == 0xffffffff
                stream.read_object('raster catalog name', allow_reference=False)
            elif ref == 7:
                assert size == 4
                stream.read_int('unknown', expected=1)
            else:
                assert False, 'Unknown property ref {}'.format(ref)

        stream.read_indexed_properties(handler)
        stream.read_ushort('unknown', expected=65535)
        stream.read_ushort('unknown', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'file_name': self.file_name,
            'path': self.path,
            'type': self.type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }
