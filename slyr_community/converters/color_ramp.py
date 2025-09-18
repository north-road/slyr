#!/usr/bin/env python

# /***************************************************************************
# color_ramp.py
# ----------
# Date                 : October 2019
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

"""
Color ramp conversion utilities
"""

from qgis.core import (
    QgsPresetSchemeColorRamp,
    QgsLimitedRandomColorRamp,
    QgsGradientColorRamp,
    QgsGradientStop,
)

from .color import ColorConverter
from ..parser.exceptions import NotImplementedException
from ..parser.objects.ramps import (
    ColorRamp,
    AlgorithmicColorRamp,
    PresetColorRamp,
    RandomColorRamp,
    MultiPartColorRamp,
)


class ColorRampConverter:
    """
    Color ramp converter
    """

    @staticmethod
    def ColorRamp_to_QgsColorRamp(ramp: ColorRamp):
        """
        Converts a ColorRamp to a QgsColorRamp
        """
        if isinstance(ramp, (PresetColorRamp,)):
            return ColorRampConverter.PresetColorRamp_to_QgsColorRamp(ramp)
        elif isinstance(ramp, (RandomColorRamp,)):
            return ColorRampConverter.RandomColorRamp_to_QgsColorRamp(ramp)
        elif isinstance(ramp, (AlgorithmicColorRamp,)):
            return ColorRampConverter.AlgorithmicColorRamp_to_QgsColorRamp(ramp)
        elif isinstance(ramp, (MultiPartColorRamp,)):
            return ColorRampConverter.MultiPartColorRamp_to_QgsColorRamp(ramp)
        else:
            raise NotImplementedException(
                "Converting {} not implemented yet".format(ramp.__class__.__name__)
            )

    @staticmethod
    def PresetColorRamp_to_QgsColorRamp(ramp: PresetColorRamp):
        """
        Converts a PresetColorRamp to a QgsColorRamp
        """
        colors = [ColorConverter.color_to_qcolor(c) for c in ramp.colors]
        out = QgsPresetSchemeColorRamp(colors)
        return out

    @staticmethod
    def RandomColorRamp_to_QgsColorRamp(ramp: RandomColorRamp):
        """
        Converts a RandomColorRamp to a QgsColorRamp
        """

        def fix_range(val) -> int:
            """
            Converts saturation/values range from 0-100 in esri symbols, to 0-255 for QGIS
            """
            return min(int(round(255 * val / 100)), 255)

        # TODO - how to correctly handle color count option?
        # TODO -- handle alpha value from CIMRandomHSVColorRamp
        out = QgsLimitedRandomColorRamp(
            count=100,
            hueMax=int(round(ramp.hue_max)),
            hueMin=int(round(ramp.hue_min)),
            satMax=fix_range(ramp.sat_max),
            satMin=fix_range(ramp.sat_min),
            valMax=fix_range(ramp.val_max),
            valMin=fix_range(ramp.val_min),
        )
        return out

    @staticmethod
    def AlgorithmicColorRamp_to_QgsColorRamp(ramp: AlgorithmicColorRamp):
        """
        Converts a AlgorithmicColorRamp to a QgsColorRamp
        """
        out = QgsGradientColorRamp(
            ColorConverter.color_to_qcolor(ramp.color1),
            ColorConverter.color_to_qcolor(ramp.color2),
        )
        return out

    # pylint: disable=too-many-branches, too-many-locals
    @staticmethod
    def MultiPartColorRamp_to_QgsColorRamp(ramp: MultiPartColorRamp):
        """
        Converts a MultiPartColorRamp to a QgsColorRamp
        """
        total_length = 0
        start_color = None
        end_color = None
        end_spec = None
        end_direction = None
        for i, p in enumerate(ramp.parts):
            if not isinstance(p, (AlgorithmicColorRamp, PresetColorRamp)):
                raise NotImplementedException(
                    "Converting MultiPartColorRamp with a {} part is not supported".format(
                        p.__class__.__name__
                    )
                )
            if len(ramp.part_lengths) > i:
                total_length += ramp.part_lengths[i]
            else:
                total_length += 1
            if not start_color:
                if isinstance(p, (AlgorithmicColorRamp,)):
                    start_color = ColorConverter.color_to_qcolor(p.color1)
                elif isinstance(p, (PresetColorRamp,)):
                    start_color = ColorConverter.color_to_qcolor(p.colors[0])
            if isinstance(p, (AlgorithmicColorRamp,)):
                end_color = ColorConverter.color_to_qcolor(p.color2)

                end_spec = None
                end_direction = None

            elif isinstance(p, (PresetColorRamp,)):
                end_color = ColorConverter.color_to_qcolor(p.colors[-1])

        out = QgsGradientColorRamp(start_color, end_color)
        if end_spec is not None:
            out.setColorSpec(end_spec)
            out.setDirection(end_direction)

        stops = []
        current_length = 0
        for i, p in enumerate(ramp.parts):
            if len(ramp.part_lengths) > i:
                this_length = ramp.part_lengths[i]
            else:
                this_length = 1

            if isinstance(p, (PresetColorRamp,)):
                color_length = this_length / len(p.colors) / total_length
                for j, c in enumerate(p.colors):
                    stops.append(
                        QgsGradientStop(
                            current_length / total_length + color_length * j,
                            ColorConverter.color_to_qcolor(c),
                        )
                    )
                    stops.append(
                        QgsGradientStop(
                            (current_length / total_length + color_length * (j + 1))
                            * 0.999999,
                            ColorConverter.color_to_qcolor(c),
                        )
                    )
            if isinstance(p, (AlgorithmicColorRamp,)):
                color1 = ColorConverter.color_to_qcolor(p.color1)
                if stops and color1.name() != stops[-1].color.name():
                    stops.append(
                        QgsGradientStop(
                            current_length * 1.0000001 / total_length,
                            ColorConverter.color_to_qcolor(p.color1),
                        )
                    )

            current_length += this_length
            current_offset = current_length / total_length
            if isinstance(p, (AlgorithmicColorRamp,)) and i < len(ramp.parts) - 1:
                stop = QgsGradientStop(
                    current_offset, ColorConverter.color_to_qcolor(p.color2)
                )
                stops.append(stop)
        out.setStops(stops)

        return out

    # pylint: enable=too-many-branches, too-many-locals
