#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import UnknownClsidException
from .feature_layer import FeatureLayer
from .units import Units


class StandaloneTable(Object):
    """
    StandaloneTable
    """

    @staticmethod
    def cls_id():
        return 'ee7c5047-e3db-11d3-a096-00c04f6bc626'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.dataset_name = None
        self.field_info = {}
        self.extensions = []
        self.description = ''
        self.display_field = ''
        self.definition_query = ''
        self.display_expression_parser = None
        self.join_type = FeatureLayer.JOIN_TYPE_LEFT_INNER
        self.join = None
        self.relations = []
        self.visible = True

        self.time_enabled = False
        self.time_zone = None
        self.time_step = 0
        self.time_step_units = Units.TIME_UNITS_UNKNOWN
        self.time_offset = 0
        self.time_offset_units = Units.TIME_UNITS_UNKNOWN
        self.time_data_changes_regularly = False
        self.time_format = ''
        self.time_display_cumulative = False
        self.time_field = ''
        self.end_time_field = ''
        self.time_extent = None

    @staticmethod
    def compatible_versions():
        return [8, 9, 10, 12, 13, 14]

    def read(self, stream: Stream, version):
        self.dataset_name = stream.read_object('dataset name')
        classes = stream.read_uint('field info count')
        for _ in range(classes):
            key = stream.read_string('key')
            self.field_info[key] = stream.read_object('field')

        self.display_field = stream.read_string('display field')

        rel_count = stream.read_int('number of relationships')
        for i in range(rel_count):
            self.relations.append(stream.read_object('relation {}'.format(i + 1)))

        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        # looks like the same shit from feature layer??
        count = stream.read_int('unknown count')
        if count == 0:
            r = 0
        elif count == 1:
            stream.read_signed_int('unknown')
        elif count == 2:
            stream.read_signed_int('unknown')
            stream.read_signed_int('unknown')
        else:
            c = 0
            last_pos = 0
            last_neg = 0
            r = stream.read_signed_int('unknown 1')
            i = 1
            done = False
            if r == 1:
                # if second number is a 1, we ignore it
                r = stream.read_signed_int('unknown 1 again')
                if r == -count:
                    done = True

            first = True
            if not done:
                while True:
                    if r == 1:
                        # went too far
                        stream.rewind(4)
                        break
                    elif r > 0:
                        if r < 10 and r < last_pos:
                            stream.rewind(4)
                            break
                        last_pos = max(r, last_pos)
                    elif r < 0:
                        last_neg = min(r, last_neg)
                    elif not first:
                        # a zero anywhere but the first digit means we've read too far
                        stream.rewind(4)
                        break

                    i += 1
                    first = False
                    r = stream.read_signed_int('unknown sequence value {}'.format(i))

        stream.read_int('unknown', expected=0)

        self.join = stream.read_object('join')
        self.name = stream.read_string('name')

        if version > 8:
            self.definition_query = stream.read_string('definition query')

        if version > 9:
            stream.read_int('unknown', expected=0)

        if version > 10:
            self.description = stream.read_string('description')
            self.display_expression_parser = stream.read_object('display expression parser')

            if version == 12:
                stream.read_ushort('unknown', expected=0)
                stream.read_object('uid')
                stream.read_object('label properties')

            # time stuff
            time_something = stream.read_ushort('unknown time related?')

            self.time_enabled = stream.read_ushort('enable time') != 0
            self.time_zone = stream.read_object('time zone')
            self.time_data_changes_regularly = stream.read_ushort('data changes regularly recalculate') != 0
            if time_something > 1:  # maybe a count??
                stream.read_ushort('unknown', expected=1)
            self.time_field = stream.read_string('time field')
            stream.read_string('unknown', expected='')
            self.time_format = stream.read_string('time format')
            stream.read_string('unknown', expected='')
            self.time_extent = stream.read_object('time extent')
            stream.read_ushort('unknown', expected=1)
            stream.read_string('unknown', expected='')
            stream.read_string('unknown', expected='')
            stream.read_ushort('unknown', expected=1)
            self.time_display_cumulative = stream.read_ushort('time display cumulative') != 0
            # time step and units
            self.time_step = stream.read_double('time step')
            self.time_step_units = stream.read_int('time step units')

            # time offset and units
            self.time_offset = stream.read_double('time offset')
            self.time_offset_units = stream.read_int('time offset units')

        if version > 13:
            remote_count = stream.read_int('remote object count')
            for i in range(remote_count):
                size = stream.read_int('size {}'.format(i)) + 20  # 20 = object header size
                pos = stream.tell()
                stream.read_int('unknown', expected=0)
                try:
                    obj = stream.read_object('remote object', allow_reference=False)
                    self.extensions.append(obj)
                    assert stream.tell() == pos + size, (size, stream.tell() - pos)
                except UnknownClsidException:
                    # don't know this object
                    stream.read(size - 20)
                # NOTE - ServerLayerExtension includes layer copyright text

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'field_format': {k: v.to_dict() for k, v in self.field_info.items()},
            'extensions': [e.to_dict() for e in self.extensions],
            'dataset_name': self.dataset_name.to_dict() if self.dataset_name else None,
            'name': self.name,
            'description': self.description,
            'display_field': self.display_field,
            'definition_query': self.definition_query,
            'display_expression_parser': self.display_expression_parser.to_dict() if self.display_expression_parser else None,
            'join': self.join.to_dict() if self.join else None,
            'relations': [r.to_dict() for r in self.relations],

            'time_enabled': self.time_enabled,
            'time_zone': self.time_zone.to_dict() if self.time_zone else None,
            'time_step': self.time_step,
            'time_step_units': Units.time_unit_to_string(self.time_step_units),
            'time_offset': self.time_offset,
            'time_offset_units': Units.time_unit_to_string(self.time_offset_units),
            'time_data_changes_regularly': self.time_data_changes_regularly,
            'time_format': self.time_format,
            'time_display_cumulative': self.time_display_cumulative,
            'time_field': self.time_field,
            'time_end_field': self.end_time_field,
            'time_extent': self.time_extent.to_dict() if self.time_extent else None,

        }
