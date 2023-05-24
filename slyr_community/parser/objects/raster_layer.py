#!/usr/bin/env python
"""
Serializable object subclass
"""

import struct

from .units import Units
from ..exceptions import UnknownClsidException, NotImplementedException
from ..object import Object
from ..stream import Stream


class RasterLayer(Object):
    """
    RasterLayer
    """

    @staticmethod
    def cls_id():
        return 'd02371c9-35f7-11d2-b1f2-00c04f8edeff'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.visible = True
        self.name = ''
        self.path = ''
        self.dataset_name = None
        self.show_map_tips = False
        self.renderer = None
        self.extensions = []
        self.zoom_max = 0
        self.zoom_min = 0
        self.show_resolution_in_toc = False
        self.extent_left = 0
        self.extent_bottom = 0
        self.extent_right = 0
        self.extent_top = 0
        self.custom_extent = None
        self.allow_interactive_display = False
        self.description = ''
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0
        self.transform = None
        self.extent = None
        self.histogram = None
        self.render_quality_percent = 100
        self.transparency = 0
        self.cached = False
        self.weight = 0.0

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

        self.joins = []
        self.relations = []

    @staticmethod
    def compatible_versions():
        return [2, 7, 11, 12, 13, 16, 17, 18]

    # pylint: disable=too-many-branches, too-many-statements
    def read(self, stream: Stream, version):
        stream.custom_props['raster_layer_version'] = version

        stream.read_ushort('unknown', expected=0)
        self.name = stream.read_string('name')
        self.path = stream.read_string('path')
        self.visible = stream.read_ushort('visible') != 0

        self.show_map_tips = stream.read_ushort('show map tips') != 0
        self.cached = stream.read_ushort('cached') != 0

        if version > 17:
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
        if version > 7:
            stream.read_int('unknown', expected=1)

        self.dataset_name = stream.read_object('dataset name')

        stream.read_string('unknown, maybe layer folder')
        if 2 < version <= 7:
            count = stream.read_int('unknown count')
            for i in range(count):
                stream.read_int('unknown')

        self.renderer = stream.read_object('renderer')

        self.zoom_max = stream.read_double('zoom max')
        self.zoom_min = stream.read_double('zoom min')

        self.transparency = stream.read_int('transparency')
        self.show_resolution_in_toc = stream.read_ushort(
            'show resolution in toc') != 0

        self.render_quality_percent = stream.read_int(
            'quality percent')  # (100=normal, 65=medium, 40=coarse)

        if version <= 2:
            return

        remote_count = stream.read_int('remote object count')
        for i in range(remote_count):
            size = stream.read_int('size {}'.format(i)) + 4
            pos = stream.tell()
            stream.read_int('unknown', expected=0)
            try:
                obj = stream.read_object('remote object', allow_reference=True)
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (size, stream.tell() - pos)
            except NotImplementedException:
                # don't know this object
                stream.read(size - 24)
            except UnknownClsidException:
                # don't know this object

                # unsure about this logic...
                if version >= 11:
                    stream.read(size - 20)
                else:
                    stream.read(size - 4)

            # NOTE - ServerLayerExtension includes layer copyright text

        self.weight = stream.read_double('layer weight', expected=200)
        self.extent_left = stream.read_double('full extent left')
        self.extent_bottom = stream.read_double('full extent bottom')
        self.extent_right = stream.read_double('full extent right')
        self.extent_top = stream.read_double('full extent top')

        number_of_joins = stream.read_int('number of joins')
        assert number_of_joins <= 1  # determine if it IS a count, or just a flag
        for i in range(number_of_joins):
            self.joins.append(stream.read_object('join'))

        number_of_relations = stream.read_int('number of relations')
        for i in range(number_of_relations):
            self.relations.append(
                stream.read_object('relation {}'.format(i + 1)))

        self.custom_extent = stream.read_object(
            'custom extent/"current setting of the layer"')

        # not quite right -- sometimes this is here in version 7 rasters.. (e.g. GlobCover_Legend.lyr), but in other
        # cases it's not (Lakes_Grd.lyr)
        # can't solve this one, so brute-force it!
        should_read_display_props = True
        start = stream.tell()
        try:
            if stream.read_ushort() not in (250, 255, 34125):
                should_read_display_props = False
            if stream.read_ushort() not in (255, 34419):
                should_read_display_props = False
            if stream.read_int() != 0:
                should_read_display_props = False
        except struct.error:
            should_read_display_props = False
        stream.seek(start)

        if should_read_display_props:

            def handler(ref, size):
                if ref == 35:
                    assert size == 2
                    stream.read_ushort('contrast')
                elif ref == 36:
                    assert size == 2
                    stream.read_ushort('brightness')
                elif ref == 37:
                    assert size == 2
                    self.allow_interactive_display = stream.read_ushort(
                        'allow interactive display') != 0
                else:
                    assert False, 'Unknown property ref {}'.format(ref)

            stream.read_indexed_properties(handler)
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)

        if version > 7:
            self.description = stream.read_string('description')
            self.stored_zoom_max = stream.read_double('stored zoom max')
            self.stored_zoom_min = stream.read_double('stored zoom min')

        if version > 11:
            self.transform = stream.read_object('transform')
            self.extent = stream.read_object('full extent of layer')

        if version > 13:
            stream.read_double('unknown', expected=0)
            stream.read_double('unknown', expected=0)

            stream.read_int('unknown', expected=0)
            time_version = stream.read_ushort('time version??',
                                              expected=(1, 2))

            # hmmm?
            if time_version >= 2:
                self.time_enabled = stream.read_ushort('time enabled') != 0
            else:
                self.time_enabled = False  # ??

            stream.read_object('time zone')
            # data changes regularly recalculate
            self.time_data_changes_regularly = stream.read_ushort(
                'has live data') != 0

            stream.read_int('unknown', expected=1)

            self.time_step = stream.read_double('time step')
            self.time_step_units = stream.read_int('time step units')
            self.time_offset = stream.read_double('time offset')
            self.time_offset_units = stream.read_int('time offset units')

            stream.read_ushort('unknown', expected=1)
            stream.read_string('time dimension name')
            stream.read_string('time dimension format')

            stream.read_double('unknown', expected=0)
            stream.read_double('unknown', expected=0)

        if version > 16:
            count = stream.read_int('number of histograms')
            for i in range(count):
                stream.read_object('histogram {}'.format(i + 1))

    # pylint: enable=too-many-branches, too-many-statements

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'visible': self.visible,
            'transparency': self.transparency,
            'zoom_min': self.zoom_min,
            'zoom_max': self.zoom_max,
            'stored_zoom_min': self.stored_zoom_min,
            'stored_zoom_max': self.stored_zoom_max,
            'file': self.name,
            'path': self.path,
            'cached': self.cached,
            'weight': self.weight,
            'dataset_name': self.dataset_name.to_dict() if self.dataset_name else None,
            'show_map_tips': self.show_map_tips,
            'renderer': self.renderer.to_dict() if self.renderer else None,
            'extensions': [e.to_dict() for e in self.extensions],
            'show_resolution_in_toc': self.show_resolution_in_toc,
            'extent_left': self.extent_left,
            'extent_bottom': self.extent_bottom,
            'extent_right': self.extent_right,
            'extent_top': self.extent_top,
            'custom_extent': self.custom_extent.to_dict() if self.custom_extent else None,
            'allow_interactive_display': self.allow_interactive_display,
            'description': self.description,
            'transform': self.transform.to_dict() if self.transform else None,
            'extent': self.extent.to_dict() if self.extent else None,
            'histogram': self.histogram.to_dict() if self.histogram else None,
            'render_quality_percent': self.render_quality_percent,
            'time_enabled': self.time_enabled,
            # 'time_zone': self.time_zone.to_dict() if self.time_zone else None,
            'time_step': self.time_step,
            'time_step_units': Units.time_unit_to_string(self.time_step_units),
            'time_offset': self.time_offset,
            'time_offset_units': Units.time_unit_to_string(
                self.time_offset_units),
            'time_data_changes_regularly': self.time_data_changes_regularly,
            # 'time_format': self.time_format,
            # 'time_display_cumulative': self.time_display_cumulative,
            # 'time_field': self.time_field,
            # 'time_end_field': self.end_time_field,
            # 'time_extent': self.time_extent.to_dict() if self.time_extent else None,
            'joins': [j.to_dict() for j in self.joins],
            'relations': [r.to_dict() for r in self.relations]
        }
