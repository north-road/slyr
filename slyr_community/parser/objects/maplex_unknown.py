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
        self.allow_border_overlap = False
        self.dictionaries = None
        self.key_number_groups = None
        self.enable_connection = False
        self.label_largest_polygon = False
        self.connection_type = 0  # esriMaplexConnectionType
        self.placement_quality = 0  # esriMaplexPlacementQuality
        self.inverted_label_tolerance = 0
        self.enable_draw_unplaced = False
        self.rotate_label_with_data_frame = False
        self.unplaced_label_color = None

    @staticmethod
    def compatible_versions():
        return [6, 7]

    def read(self, stream, version):
        self.placement_quality = stream.read_int('placement quality')
        self.allow_border_overlap = stream.read_ushort('allow border overlap') != 0
        self.dictionaries = stream.read_object('dictionaries')
        self.enable_connection = stream.read_ushort('enable connection') != 0
        self.connection_type = stream.read_int('connection type')
        self.inverted_label_tolerance = stream.read_double('inverted label tolerance')
        self.unplaced_label_color = stream.read_object('unplaced label color')
        self.label_largest_polygon = stream.read_ushort('label largest polygon') != 0
        self.enable_draw_unplaced = stream.read_ushort('enable draw unplaced') != 0
        self.rotate_label_with_data_frame = stream.read_ushort('rotate label with data frame') != 0

        if version > 6:
            self.key_number_groups = stream.read_object('key number groups')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'allow_border_overlap': self.allow_border_overlap,
            'dictionaries': self.dictionaries.to_dict() if self.dictionaries else None,
            'enable_connection': self.enable_connection,
            'key_number_groups': self.key_number_groups.to_dict() if self.key_number_groups else None,
            'unplaced_label_color': self.unplaced_label_color.to_dict() if self.unplaced_label_color else None,
            'label_largest_polygon': self.label_largest_polygon,
            'connection_type': self.connection_type,
            'placement_quality': self.placement_quality,
            'inverted_label_tolerance': self.inverted_label_tolerance,
            'enable_draw_unplaced': self.enable_draw_unplaced,
            'rotate_label_with_data_frame': self.rotate_label_with_data_frame
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
        self.name = ''
        self.horizontal_alignment = 0  # esriMaplexKeyNumberHorizontalAlignment
        self.minimum_number_of_lines = 0
        self.maximum_number_of_lines = 0
        self.delimiter_character = ''
        self.number_reset_type = 0  # esriMaplexKeyNumberResetType

    def read(self, stream, version):
        self.name = stream.read_string('name')
        self.horizontal_alignment = stream.read_int('horizontal alignment')
        self.minimum_number_of_lines = stream.read_int('minimum number of lines')
        self.maximum_number_of_lines = stream.read_int('maximum number of lines')
        self.delimiter_character = stream.read_string('delimiter character')
        self.number_reset_type = stream.read_int('number reset type')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'horizontal_alignment': self.horizontal_alignment,
            'minimum_number_of_lines': self.minimum_number_of_lines,
            'maximum_number_of_lines': self.maximum_number_of_lines,
            'delimiter_character': self.delimiter_character,
            'number_reset_type': self.number_reset_type
        }


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
