#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import UnknownClsidException, NotImplementedException


class PageLayout(Object):
    """
    PageLayout
    """

    @staticmethod
    def cls_id():
        return "dd94d76e-836d-11d0-87ec-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.elements = []
        self.page = None
        self.ruler_settings = None
        self.snap_grid = None
        self.vertical_snap_guides = None
        self.horizontal_snap_guides = None
        self.conserve_memory = False
        self.delay_background_draw = False
        self.verbose_events = False
        self.is_map_activated = False
        self.show_rulers = False
        self.align_to_margins = False
        self.output_band_size = 0
        self.page_index = None

        self.extensions = []

    @staticmethod
    def compatible_versions():
        return [5, 6, 7, 9, 10, 14, 15]

    def __repr__(self):
        if self.ref_id is not None:
            return "<PageLayout: ({})>".format(self.ref_id)
        else:
            return "<PageLayout>"

    def read(self, stream: Stream, version):
        stream.read_int("unknown", expected=(1, 7, 8))

        count = stream.read_int("element count??")
        for i in range(count):
            if version > 6:
                size = stream.read_int("size of element {}".format(i + 1))
                stream.read_int("unknown", expected=0)  # maybe some element flags?
            else:
                size = None

            start = stream.tell()
            self.elements.append(stream.read_object("element {}".format(i + 1)))
            if version > 6:
                assert stream.tell() == size + start, "Expected size {}, got {}".format(
                    size, stream.tell() - start
                )

        self.page = stream.read_object("page")
        self.ruler_settings = stream.read_object("ruler settings")
        self.snap_grid = stream.read_object("snap grid")
        self.horizontal_snap_guides = stream.read_object("horizontal snap guides")
        self.vertical_snap_guides = stream.read_object("vertical snap guides")

        stream.read_ushort("unknown", expected=1)
        stream.read_double(
            "unknown"
        )  # , expected=(0.2, 0.5, 0.508001, 0.5080010160020321))
        count = stream.read_int("count")
        for i in range(count):
            stream.read_raw_clsid(
                "guide snap {}".format(i),
                expected="fc27fab1-db88-11d1-8778-0000f8751720",
            )
        count = stream.read_int("count")
        for i in range(count):
            stream.read_raw_clsid(
                "unknown {}".format(i + 1),
                expected=(
                    "fc27fab1-db88-11d1-8778-0000f8751720",
                    "fc27fab2-db88-11d1-8778-0000f8751720",
                    "fc27fab3-db88-11d1-8778-0000f8751720",
                    "fc27fab0-db88-11d1-8778-0000f8751720",
                ),
            )

        stream.read_object("unknown map", expect_existing=True)

        self.is_map_activated = stream.read_ushort("is map activated") != 0
        self.show_rulers = stream.read_ushort("show rulers") != 0
        self.verbose_events = stream.read_ushort("verbose events") != 0
        self.align_to_margins = stream.read_ushort("align to margins") != 0

        # maybe last view extent?
        stream.read_double("unknown")  # , expected=-1.0500804334942013)
        stream.read_double("unknown")  # , expected=-1.4850563034459419)
        stream.read_double("unknown")  # , expected=22.05168910337821)
        stream.read_double("unknown")  # , expected=31.18618237236475)

        stream.read_double("unknown")  # , expected=(0, 0.42333418000169337))
        stream.read_double("unknown")  # , expected=(0, 0.43180086360172726))
        stream.read_double(
            "unknown"
        )  # , expected=(8.5, 21.59004318008636, 21.001608669884007, 20.150706968080602))
        stream.read_double(
            "unknown"
        )  # , expected=(11.0, 27.940055880111764, 29.70112606891881, 28.84599102531539))

        self.conserve_memory = stream.read_ushort("conserve memory") != 0
        stream.read_ushort("unknown", expected=0)
        self.output_band_size = stream.read_ushort("output band size")
        stream.read_ushort("unknown", expected=0)
        self.delay_background_draw = stream.read_ushort("delay background draw") != 0
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=32)
        if version < 6:
            return

        stream.read_int("unknown", expected=(1, 2, 3))
        if version < 7:
            return

        stream.read_ushort("unknown", expected=65535)
        if version < 8:
            return

        stream.read_ushort("unknown", expected=65535)
        stream.read_ushort("unknown", expected=0)

        if version < 10:
            return

        remote_count = stream.read_int("remote object count")
        for i in range(remote_count):
            size = stream.read_int("size {}".format(i)) + 20  # 20 = object header size
            pos = stream.tell()
            stream.read_int("unknown", expected=0)

            if size == 20:
                stream.read_raw_clsid("Empty object ref")
                continue

            try:
                obj = stream.read_object(
                    "remote object", allow_reference=False, expected_size=size
                )
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (
                    "Expected length {} got length {}".format(size, stream.tell() - pos)
                )
            except UnknownClsidException:
                # don't know this object
                stream.read(size - 20)
            except NotImplementedException:
                # don't know this object
                stream.read(size - 20)

        if version <= 10:
            return  # hmm, todo!
        size = stream.read_int("size?") + 4
        pos = stream.tell()
        stream.read_int("unknown", expected=0)
        self.page_index = stream.read_object("page index")
        assert stream.tell() == size + pos, (stream.tell() - pos, size)

        stream.read_int("unknown", expected=0)

        count = stream.read_int("data frame count?")
        for i in range(count):
            stream.read_int("unknown {}".format(i + 1), expected=0)

        if version > 14:
            for i in range(count):
                stream.read_object("envelope")
                stream.read_double("unknown")  # 0.5, 0.74,...

            # count = stream.read_ushort('printer count?')
            # for i in range(count):
            #    stream.read_ushort('unknown', expected=3)
            #    stream.read_ushort('unknown', expected=2)
            #    stream.read_string('printer name')
            #    # ...

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "elements": [e.to_dict() for e in self.elements],
            "page": self.page.to_dict() if self.page else None,
            "ruler_settings": self.ruler_settings.to_dict()
            if self.ruler_settings
            else None,
            "snap_grid": self.snap_grid.to_dict() if self.snap_grid else None,
            "vertical_snap_guides": self.vertical_snap_guides.to_dict()
            if self.vertical_snap_guides
            else None,
            "horizontal_snap_guides": self.horizontal_snap_guides.to_dict()
            if self.horizontal_snap_guides
            else None,
            "extensions": [e.to_dict() for e in self.extensions],
            "conserve_memory": self.conserve_memory,
            "delay_background_draw": self.delay_background_draw,
            "verbose_events": self.verbose_events,
            "is_map_activated": self.is_map_activated,
            "show_rulers": self.show_rulers,
            "align_to_margins": self.align_to_margins,
            "output_band_size": self.output_band_size,
            "page_index": self.page_index.to_dict() if self.page_index else None,
        }
