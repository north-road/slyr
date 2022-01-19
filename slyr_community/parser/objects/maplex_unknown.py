#!/usr/bin/env python
"""
Serializable object subclass

"""

from ..object import Object


class MaplexDictionaries(Object):
    """
    MaplexLayerSettings
    """

    @staticmethod
    def cls_id():
        return '20664808-56db-bd28-67dc-02e33decf321'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.dictionaries = []

    def read(self, stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.dictionaries.append(stream.read_object('Dictionary {}'.format(i + 1)))

    def to_dict(self):
        return {
            'dictionaries': [e.to_dict() for e in self.dictionaries]
        }


class MaplexDictionary(Object):
    """
    MaplexDictionary
    """

    @staticmethod
    def cls_id():
        return '20664808-3de2-1cd1-8a09-08e00dec7321'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.entries = []
        self.name = ''

    @staticmethod
    def compatible_versions():
        return [1, 2, 3]

    def read(self, stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.entries.append(stream.read_object('Entry {}'.format(i + 1)))
        self.name = stream.read_string('name')

    def to_dict(self):
        return {
            'name': self.name,
            'entries': [e.to_dict() for e in self.entries]
        }


class MaplexDictionaryEntry(Object):
    """
    MaplexLayerSettings
    """

    @staticmethod
    def cls_id():
        return '20664808-fe45-9018-be1f-66eb0dec7321'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.type = 0  # esriMaplexAbbrevTypeEnding
        self.text = ''
        self.abbreviation = ''

    @staticmethod
    def compatible_versions():
        return [1, 3]

    def read(self, stream, version):
        self.text = stream.read_string('text')
        self.abbreviation = stream.read_string('abbreviation')
        self.type = stream.read_int('type')

    def to_dict(self):
        return {
            'text': self.text,
            'abbrevation': self.abbreviation,
            'type': self.type
        }


class MaplexOverposterProperties(Object):
    """
    MaplexOverposterProperties
    """

    @staticmethod
    def cls_id():
        return '20664808-a8c2-c1d1-acdc-1708f95c7321'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.dictionaries = None
        self.key_number_groups = None

    @staticmethod
    def compatible_versions():
        return [6, 7]

    def read(self, stream, version):
        stream.read_int('unknown', expected=1)
        stream.read_ushort('unknown', expected=0)
        self.dictionaries = stream.read_object('dictionaries')
        stream.read_ushort('unknown flag', expected=65535)
        stream.read_int('unknown', expected=1)
        stream.read_double('unknown', expected=2)
        stream.read_object('unknown color')
        stream.read_ushort('unknown flag', expected=65535)
        stream.read_int('unknown', expected=0)
        if version > 6:
            self.key_number_groups = stream.read_object('key number groups')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'dictionaries': self.dictionaries.to_dict() if self.dictionaries else None,
            'key_number_groups': self.key_number_groups.to_dict() if self.key_number_groups else None
        }


class MaplexPlacedLabel(Object):
    """
    MaplexLayerSettings
    """

    @staticmethod
    def cls_id():
        return '20664808-4eb1-1fab-823d-1ca3b6ed938d'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3]


class MaplexKeyNumberGroups(Object):
    """
    MaplexKeyNumberGroups
    """

    @staticmethod
    def cls_id():
        return '755f3bb8-63fb-e54b-884c-74f3dd2a8a81'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.groups = []

    def read(self, stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.groups.append(stream.read_object('group {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'groups': [g.to_dict() for g in self.groups]
        }


class MaplexKeyNumberGroup(Object):
    """
    MaplexKeyNumberGroup
    """

    @staticmethod
    def cls_id():
        return '66ddef5d-1ab3-5f31-7bc1-755ddef33d32'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream, version):
        stream.read_string('name?')
        stream.read_int('unknown', expected=1)
        stream.read_int('unknown', expected=2)
        stream.read_int('unknown', expected=20)
        stream.read_string('unknown', expected='.')
        stream.read_int('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {}


class MaplexAnnotateFeature(Object):
    """
    MaplexLayerSettings
    """

    @staticmethod
    def cls_id():
        return '20664808-c2f5-1dd2-9a30-0ec04f6bc630'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3]


class MaplexAnnotateMap(Object):
    """
    MaplexLayerSettings
    """

    @staticmethod
    def cls_id():
        return '20664808-14ec-11d2-a27e-080009b6f22b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3]


class MaplexOverposter(Object):
    """
    MaplexLayerSettings
    """

    @staticmethod
    def cls_id():
        return '20664808-38e2-11d1-8809-080009ec732a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [3]
