#!/usr/bin/env python

# /***************************************************************************
# geometry.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/
import math
from typing import List

from qgis.PyQt.QtCore import QRectF, QPointF, QLineF
from qgis.PyQt.QtGui import QPainterPath, QTransform
from qgis.core import (
    QgsGeometry,
    QgsLineString,
    QgsPolygon,
    QgsPoint,
    QgsCircularString,
    QgsCurve,
    QgsCompoundCurve,
    QgsCurvePolygon,
    QgsMultiPoint,
    QgsMultiCurve,
)

from ..parser.exceptions import NotImplementedException
from ..parser.objects.geometry import Segment
from ..parser.objects.point import Point
from ..parser.objects.polygon import Polygon
from ..parser.objects.polyline import Polyline
from ..parser.objects.multipoint import Multipoint
from ..parser.objects.geometry_bag import GeometryBag


class GeometryConverter:
    @staticmethod
    def convert_geometry(geometry) -> QgsGeometry:
        if isinstance(geometry, Point):
            return GeometryConverter.point_to_geometry(geometry)
        if isinstance(geometry, Multipoint):
            return GeometryConverter.multipoint_to_geometry(geometry)
        if isinstance(geometry, Polyline):
            return GeometryConverter.polyline_to_geometry(geometry)
        if isinstance(geometry, Polygon):
            return GeometryConverter.polygon_to_geometry(geometry)
        if isinstance(geometry, GeometryBag):
            return GeometryConverter.geometry_bag_to_geometry(geometry)

        return QgsGeometry()

    @staticmethod
    def point_to_geometry(point: Point) -> QgsGeometry:
        """
        Convert a point object to a QGIS geometry
        """
        p = QgsPoint(point.x, point.y)
        if point.z is not None:
            p.addZValue(point.z)
        if point.m is not None:
            p.addMValue(point.m)
        return QgsGeometry(p)

    @staticmethod
    def geometry_bag_to_geometry(geometry: GeometryBag) -> QgsGeometry:
        geometries = [
            GeometryConverter.convert_geometry(g) for g in geometry.geometries
        ]
        return QgsGeometry.collectGeometry(geometries)

    @staticmethod
    def multipoint_to_geometry(geometry: Multipoint) -> QgsGeometry:
        """
        Convert a multipoint to a QGIS geometry
        """
        res = QgsMultiPoint()
        for p in geometry.points:
            # TODO -- handle z/m, when examples found
            res.addGeometry(QgsPoint(*p))
        return QgsGeometry(res)

    @staticmethod
    def is_clockwise_arc(p1: QgsPoint, p2: QgsPoint, center: QgsPoint) -> bool:
        """
        Returns True if the shortest path from p1 to p2 on the circle
        with center is clockwise
        """
        # Calculate vectors from center to points
        v1 = p1 - center
        v2 = p2 - center

        # Calculate z-component of the cross product
        cross_product_z = v1.crossProduct(v2)

        # If cross product is negative, the direction is clockwise
        return cross_product_z < 0

    @staticmethod
    def circular_string_from_two_points_and_center(
        p1: QgsPoint, p2: QgsPoint, center: QgsPoint, is_counter_clockwise: bool
    ) -> QgsCircularString:
        """
        Creates a circular string from two points and center
        """
        shortest_path_is_cw = GeometryConverter.is_clockwise_arc(p1, p2, center)

        if is_counter_clockwise:
            use_shortest_arc = not shortest_path_is_cw
        else:
            use_shortest_arc = shortest_path_is_cw

        return QgsCircularString.fromTwoPointsAndCenter(
            p1, p2, center, use_shortest_arc
        )

    @staticmethod
    def convert_to_curve(
        ring, segments: List[Segment], is_ring: bool, part_start_index: int = 0
    ) -> QgsCurve:
        if not segments:
            # nice and easy, a LineString
            return QgsLineString([QgsPoint(x, y) for (x, y) in ring])

        # else, some other thing, or mix of things. woot.
        compound_curve = QgsCompoundCurve()

        # shapes with curves must be enlarged before conversion to QPolygonF, or
        # the curves are approximated too much and appear jaggy
        t = QTransform.fromScale(100, 100)
        # inverse transform used to scale created polygons back to expected size
        ti, _ = t.inverted()

        for i, p in enumerate(ring[:-1]):
            start = QgsPoint(p[0], p[1])
            end = QgsPoint(ring[i + 1][0], ring[i + 1][1])

            start_point_index = i + part_start_index
            this_segment = None
            for segment in segments:
                if segment.start_point_index == start_point_index:
                    this_segment = segment
            if this_segment is None:
                # linear segment
                compound_curve.addCurve(QgsLineString(start, end))
            elif this_segment.segment_type == Segment.SEGMENT_LINE:
                compound_curve.addCurve(QgsLineString(start, end))
            elif this_segment.segment_type == Segment.SEGMENT_ARC_INTERIOR_POINT:
                compound_curve.addCurve(
                    QgsCircularString(
                        start,
                        QgsPoint(this_segment.vertex[0], this_segment.vertex[1]),
                        end,
                    )
                )
            elif this_segment.segment_type == Segment.SEGMENT_ARC_CENTER_POINT:
                is_ccw = this_segment.is_ccw
                center = QgsPoint(*this_segment.vertex)
                compound_curve.addCurve(
                    GeometryConverter.circular_string_from_two_points_and_center(
                        start, end, center, is_ccw
                    )
                )
            elif this_segment.segment_type == Segment.SEGMENT_BEZIER:
                compound_curve.addCurve(
                    QgsLineString.fromBezierCurve(
                        start,
                        QgsPoint(this_segment.cp1[0], this_segment.cp1[1]),
                        QgsPoint(this_segment.cp2[0], this_segment.cp2[1]),
                        end,
                        10,
                    )
                )
            # elif Qgis.QGIS_VERSION_INT >= 30900 and segments[i].segment_type == Segment.SEGMENT_BEZIER:
            #     compound_curve.addCurve(QgsLineString.fromEllipticArc(QgsPoint(segments[i].center[0],segments[i].center[1]),
            #                                                           segments[i].radius_major_axis * 2,
            #                                                           segments[i].radius_major_axis * segments[i].minor_major_ratio * 2,
            #                                                           segments[i].rotation,
            #                                                           QgsPoint(segments[i].cp1[0],segments[i].cp1[1]),
            #                                                           QgsPoint(segments[i].cp2[0],
            #                                                                    segments[i].cp2[1]), end, 10))
            elif this_segment.segment_type == Segment.SEGMENT_ELLIPTICAL_ARC:
                path = QPainterPath()
                path.moveTo(start.x(), start.y())

                if this_segment.rotation != 0:
                    raise NotImplementedException(
                        "Converting rotated ellipsis is not currently supported"
                    )

                center = QPointF(this_segment.center[0], this_segment.center[1])

                start_angle = QLineF(center, QPointF(start.x(), start.y())).angle()
                end_angle = QLineF(center, QPointF(end.x(), end.y())).angle()

                width = this_segment.radius_major_axis * 2
                height = width * this_segment.minor_major_ratio
                path.arcTo(
                    QRectF(
                        center.x() - width / 2.0,
                        center.y() - height / 2.0,
                        width,
                        height,
                    ),
                    start_angle,
                    (end_angle - start_angle + 360) % 360 if start != end else 360,
                )

                segmented = path.toFillPolygon(t)
                segmented = ti.map(segmented)

                # this is gross, but toFillPolygon force closes the polyline! argh
                if not is_ring:
                    last_i = None
                    for i, p in enumerate(segmented):
                        if (
                            abs(p.x() - end.x()) < 0.0000000001
                            and abs(p.y() - end.y()) < 0.0000000001
                        ):
                            last_i = i
                    assert last_i is not None

                    segmented = segmented[:last_i]

                compound_curve.addCurve(
                    QgsLineString([QgsPoint(p.x(), p.y()) for p in segmented])
                )

        # try to simplify curve if all parts are circular strings
        all_curves = [
            compound_curve.curveAt(i) for i in range(compound_curve.nCurves())
        ]
        if all_curves and all(
            [isinstance(curve, QgsCircularString) for curve in all_curves]
        ):
            new_curve = all_curves[0].clone()
            for curve in all_curves[1:]:
                new_curve.append(curve)

            return new_curve

        return compound_curve

    @staticmethod
    def polygon_to_geometry(polygon: Polygon) -> QgsGeometry:
        """
        Converts a polygon to a QGIS geometry
        """
        if not polygon.parts:
            return QgsGeometry()

        if len(polygon.parts) > 1:
            parts = []
            part_start_index = 0
            for part in polygon.parts:
                parts.append(
                    GeometryConverter.convert_polygon(
                        part, polygon.segments, part_start_index
                    )
                )
                part_start_index += len(part)

            res = QgsGeometry.collectGeometry(parts)
            return res

        return GeometryConverter.convert_polygon(polygon.parts[0], polygon.segments)

    @staticmethod
    def convert_polygon(polygon, segments, part_start_index: int = 0) -> QgsGeometry:
        exterior = GeometryConverter.convert_to_curve(
            polygon, segments, True, part_start_index
        )
        if isinstance(exterior, QgsLineString):
            res = QgsPolygon()
            res.setExteriorRing(exterior)
        else:
            res = QgsCurvePolygon()
            res.setExteriorRing(exterior)
        return QgsGeometry(res)

    @staticmethod
    def polyline_to_geometry(polyline: Polyline) -> QgsGeometry:
        """
        Converts a polyline to a QGIS geometry
        """
        if not polyline.parts:
            return QgsGeometry(QgsLineString())

        if len(polyline.parts) > 1:
            multi_curve = QgsMultiCurve()
            part_start_index = 0
            for part in polyline.parts:
                multi_curve.addGeometry(
                    GeometryConverter.convert_to_curve(
                        part, polyline.segments, False, part_start_index
                    )
                )
                part_start_index += len(part)

            return QgsGeometry(multi_curve)

        exterior = GeometryConverter.convert_to_curve(
            polyline.parts[0], polyline.segments, False
        )
        return QgsGeometry(exterior)

    @staticmethod
    def angle_on_ellipse(
        point_on_arc_x: float,
        point_on_arc_y: float,
        center_x: float,
        center_y: float,
        rotation_degrees: float,
        semi_major: float,
        semi_minor: float,
    ):
        if semi_major == 0 or semi_minor == 0:
            return 0

        rotation_radians = math.radians(rotation_degrees)
        cos_rot = math.cos(rotation_radians)
        sin_rot = math.sin(rotation_radians)
        delta_x = point_on_arc_x - center_x
        delta_y = point_on_arc_y - center_y
        cos_a = (cos_rot * delta_x - sin_rot * delta_y) / semi_major
        sin_a = (sin_rot * delta_x + cos_rot * delta_y) / semi_minor
        angle = math.degrees(math.atan2(sin_a, cos_a))
        if angle < -180:
            return angle + 360
        return angle

    @staticmethod
    def approximate_arc_angles(
        center_x: float,
        center_y: float,
        center_z: float,
        primary_radius: float,
        secondary_radius: float,
        rotation: float,
        start_angle: float,
        end_angle: float,
        max_angle_step_size_degrees: float,
        is_minor,
        use_max_gap: bool = False,
    ):
        line = QgsLineString()
        out_x = []
        out_y = []

        rotation_radians = math.radians(rotation)
        if max_angle_step_size_degrees < 1e-6:
            max_angle_step_size_degrees = 4

        max_interpolation_gap = 0 if use_max_gap else 0
        is_full_circle = math.fabs(end_angle - start_angle) == 360.0

        start_angle *= -1
        end_angle *= -1

        vertex_count = max(
            2,
            math.ceil(math.fabs(end_angle - start_angle) / max_angle_step_size_degrees)
            + 1,
        )
        slice = (end_angle - start_angle) / (vertex_count - 1)
        if is_full_circle:
            vertex_count -= 1

        last_x = 0
        last_y = 0
        total_add_points = 0
        for point in range(vertex_count):
            angle_on_ellipse = math.radians(start_angle + point * slice)
            ellipse_x = math.cos(angle_on_ellipse) * primary_radius
            ellipse_y = math.sin(angle_on_ellipse) * secondary_radius

            if point and max_interpolation_gap != 0:
                dist_from_last = math.sqrt(
                    (last_x - ellipse_x) ** 2 + (last_y - ellipse_y) ** 2
                )

                if dist_from_last > max_interpolation_gap:
                    add_points = int(dist_from_last / max_interpolation_gap)
                    add_slice = slice / (add_points + 1)
                    for add_point in range(add_points):
                        add_angle_on_ellipse = math.radians(
                            start_angle
                            + (point - 1) * slice
                            + (add_point + 1) * add_slice
                        )
                        out_x.append(math.cos(add_angle_on_ellipse) * primary_radius)
                        out_y.append(math.sin(add_angle_on_ellipse) * secondary_radius)

                    total_add_points += add_points
            out_x.append(ellipse_x)
            out_y.append(ellipse_y)

            last_x = ellipse_x
            last_y = ellipse_y

        out_arc_x = []
        out_arc_y = []
        vertex_count = len(out_x)
        for point in range(vertex_count):
            ellipse_x = out_x[point]
            ellipse_y = out_y[point]

            arc_x = (
                center_x
                + ellipse_x * math.cos(rotation_radians)
                + ellipse_y * math.sin(rotation_radians)
            )
            arc_y = (
                center_y
                - ellipse_x * math.sin(rotation_radians)
                + ellipse_y * math.cos(rotation_radians)
            )

            out_arc_x.append(arc_x)
            out_arc_y.append(arc_y)

        if is_full_circle:
            out_arc_x.append(out_arc_x[0])
            out_arc_y.append(out_arc_y[0])

        return QgsLineString(out_arc_x, out_arc_y)

    @staticmethod
    def convert_ellipse_by_center(
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        center_x: float,
        center_y: float,
        rotation_degrees: float,
        semi_major: float,
        ratio_semi_minor: float,
        is_minor: bool,
        is_complete: bool,
    ):
        """
        Converts an ellipse to a linestring
        """
        semi_minor = semi_major * ratio_semi_minor
        rotation_degrees = -rotation_degrees
        angle_start = GeometryConverter.angle_on_ellipse(
            start_x,
            start_y,
            center_x,
            center_y,
            rotation_degrees,
            semi_major,
            semi_minor,
        )
        angle_end = GeometryConverter.angle_on_ellipse(
            end_x, end_y, center_x, center_y, rotation_degrees, semi_major, semi_minor
        )
        angle_start_for_approx = -angle_start
        angle_end_for_approx = -angle_end
        if is_complete:
            angle_end_for_approx = angle_start_for_approx + 360
        elif is_minor:
            if angle_end_for_approx > angle_start_for_approx + 180:
                angle_end_for_approx -= 360
            elif angle_end_for_approx < angle_start_for_approx - 180:
                angle_end_for_approx += 360
        else:
            if (
                angle_end_for_approx > angle_start_for_approx
                and angle_end_for_approx < angle_start_for_approx + 180
            ):
                angle_end_for_approx -= 360
            elif (
                angle_end_for_approx < angle_start_for_approx
                and angle_end_for_approx > angle_start_for_approx - 180
            ):
                angle_end_for_approx += 360

        line = GeometryConverter.approximate_arc_angles(
            center_x,
            center_y,
            0,
            semi_major,
            semi_minor,
            rotation_degrees,
            angle_start_for_approx,
            angle_end_for_approx,
            is_minor,
            0,
        )

        line.setXAt(0, start_x)
        line.setYAt(0, start_y)
        line.setXAt(line.numPoints() - 1, end_x)
        line.setYAt(line.numPoints() - 1, end_y)

        return line
