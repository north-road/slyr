#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..exceptions import NotImplementedException, UnreadableSymbolException
from ..object import Object
from ..stream import Stream


class Segment:
    """
    Represents a line segment
    """

    SEGMENT_ARC = 1
    SEGMENT_LINE = 2
    SEGMENT_SPIRAL = 3
    SEGMENT_BEZIER = 4
    SEGMENT_ELLIPTICAL_ARC = 5

    @staticmethod
    def segment_type_to_string(segment_type):
        """
        Converts a segment type to string
        """
        if segment_type == Segment.SEGMENT_ARC:
            return "arc"
        elif segment_type == Segment.SEGMENT_LINE:
            return "line"
        elif segment_type == Segment.SEGMENT_SPIRAL:
            return "spiral"
        elif segment_type == Segment.SEGMENT_BEZIER:
            return "bezier"
        elif segment_type == Segment.SEGMENT_ELLIPTICAL_ARC:
            return "elliptical_arc"
        else:
            assert False

    def __init__(self, segment_type, **kwargs):
        self.segment_type = segment_type

        self.vertex = kwargs.get("vertex", None)

        # for bezier curves
        self.cp1 = kwargs.get("cp1", None)
        self.cp2 = kwargs.get("cp2", None)

        # for elliptical arcs
        self.center = kwargs.get("center", None)
        self.radius_major_axis = kwargs.get("radius_major_axis", None)
        self.minor_major_ratio = kwargs.get("minor_major_ratio", None)
        self.rotation = kwargs.get("rotation", None)

    def to_dict(self):  # pylint: disable=method-hidden,missing-function-docstring
        res = {
            "type": Segment.segment_type_to_string(self.segment_type),
        }

        if self.segment_type == Segment.SEGMENT_ARC:
            res["vertex"] = self.vertex
        elif self.segment_type == Segment.SEGMENT_BEZIER:
            res["cp1"] = self.cp1
            res["cp2"] = self.cp2
        elif self.segment_type == Segment.SEGMENT_ELLIPTICAL_ARC:
            res["center"] = self.center
            res["radius_major_axis"] = self.radius_major_axis
            res["minor_major_ratio"] = self.minor_major_ratio
            res["rotation"] = self.rotation

        return res


class Geometry(Object):
    """
    Geometry base
    """

    GEOMETRY_NULL = 0
    GEOMETRY_POINT = 1
    GEOMETRY_MULTIPOINT = 2
    GEOMETRY_POLYLINE = 3
    GEOMETRY_POLYGON = 4
    GEOMETRY_ENVELOPE = 5
    GEOMETRY_PATH = 6
    GEOMETRY_ANY = 7
    GEOMETRY_MULTIPATCH = 9
    GEOMETRY_RING = 11
    GEOMETRY_LINE = 13
    GEOMETRY_CIRCULAR_ARC = 14
    GEOMETRY_BEZIER_CURVE = 15
    GEOMETRY_ELLIPTIC_ARC = 16
    GEOMETRY_BAG = 17
    GEOMETRY_TRIANGLE_STRIP = 18
    GEOMETRY_TRIANGLE_FAN = 19
    GEOMETRY_RAY = 20
    GEOMETRY_SPHERE = 21
    GEOMETRY_TRIANGLES = 22

    GEOMETRY_TYPE_TO_STRING = {
        GEOMETRY_NULL: "null",
        GEOMETRY_POINT: "point",
        GEOMETRY_MULTIPOINT: "multipoint",
        GEOMETRY_POLYLINE: "polyline",
        GEOMETRY_POLYGON: "polygon",
        GEOMETRY_ENVELOPE: "envelope",
        GEOMETRY_PATH: "path",
        GEOMETRY_ANY: "any",
        GEOMETRY_MULTIPATCH: "multipatch",
        GEOMETRY_RING: "ring",
        GEOMETRY_LINE: "line",
        GEOMETRY_CIRCULAR_ARC: "circular_arc",
        GEOMETRY_BEZIER_CURVE: "bezier_curve",
        GEOMETRY_ELLIPTIC_ARC: "elliptic_arc",
        GEOMETRY_BAG: "bag",
        GEOMETRY_TRIANGLE_STRIP: "triangle_strip",
        GEOMETRY_TRIANGLE_FAN: "triangle_fan",
        GEOMETRY_RAY: "ray",
        GEOMETRY_SPHERE: "sphere",
        GEOMETRY_TRIANGLES: "triangles",
    }

    @staticmethod
    def geometry_type_to_string(geometry_type) -> str:
        """
        Converts a geometry type to string
        """
        return Geometry.GEOMETRY_TYPE_TO_STRING[geometry_type]

    @staticmethod
    def string_to_geometry_type(string: str):
        """
        Finds a geometry type by string
        """
        return [k for k, v in Geometry.GEOMETRY_TYPE_TO_STRING.items() if v == string][
            0
        ]

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.crs = None
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        self.segments = []

    def read_curve_points(self, stream: Stream):
        """
        Reads geometry curve points
        """
        count = stream.read_int("curve point count")
        curve_points = []

        for i in range(count):
            stream.read_int("associated index {}".format(i + 1))  # , expected=i)
            segment_type = stream.read_int("segment type")

            if segment_type == Segment.SEGMENT_ELLIPTICAL_ARC:
                x = stream.read_double("center x")
                y = stream.read_double("center y")
                rotation = stream.read_double("rotation radians counterclockwise")
                radius_major_axis = stream.read_double("radius_major_axis")
                minor_major_ratio = stream.read_double("minor_major_ratio")

                curve_points.append(
                    Segment(
                        Segment.SEGMENT_ELLIPTICAL_ARC,
                        center=[x, y],
                        radius_major_axis=radius_major_axis,
                        minor_major_ratio=minor_major_ratio,
                        rotation=rotation,
                    )
                )

                stream.read_int("unknown", expected=(24578, 24638))

            elif segment_type == Segment.SEGMENT_ARC:
                # circular arc
                x = stream.read_double("x")
                y = stream.read_double("y")
                curve_points.append(Segment(Segment.SEGMENT_ARC, vertex=[x, y]))

                stream.read_int("unknown", expected=390)

            elif segment_type == Segment.SEGMENT_BEZIER:
                x1 = stream.read_double("x1")
                y1 = stream.read_double("y1")
                x2 = stream.read_double("x2")
                y2 = stream.read_double("y2")
                curve_points.append(
                    Segment(Segment.SEGMENT_BEZIER, cp1=[x1, y1], cp2=[x2, y2])
                )

            elif segment_type == Segment.SEGMENT_LINE:
                raise NotImplementedException("Cannot read line segment types")
            elif segment_type == Segment.SEGMENT_SPIRAL:
                raise NotImplementedException("Cannot read spiral segment types")
            else:
                raise UnreadableSymbolException(
                    "Unknown segment type: {}".format(segment_type)
                )

        self.segments = curve_points

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "crs": self.crs.to_dict() if self.crs else None,
            "x_min": self.x_min,
            "y_min": self.y_min,
            "x_max": self.x_max,
            "y_max": self.y_max,
            "segments": [s.to_dict() for s in self.segments],
        }
