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
from qgis.core import (QgsPresetSchemeColorRamp,
                       QgsLimitedRandomColorRamp,
                       QgsGradientColorRamp,
                       QgsGradientStop)
from slyr_community.parser.exceptions import NotImplementedException
from slyr_community.parser.objects.ramps import (
    ColorRamp,
    AlgorithmicColorRamp,
    PresetColorRamp,
    RandomColorRamp,
    MultiPartColorRamp
)
from slyr_community.converters.color import ColorConverter


class ColorRampConverter:

    @staticmethod
    def ColorRamp_to_QgsColorRamp(ramp: ColorRamp):
        """
        Converts a ColorRamp to a QgsColorRamp
        """
        if isinstance(ramp, PresetColorRamp):
            return ColorRampConverter.PresetColorRamp_to_QgsColorRamp(ramp)
        elif isinstance(ramp, RandomColorRamp):
            return ColorRampConverter.RandomColorRamp_to_QgsColorRamp(ramp)
        elif isinstance(ramp, AlgorithmicColorRamp):
            return ColorRampConverter.AlgorithmicColorRamp_to_QgsColorRamp(ramp)
        elif isinstance(ramp, MultiPartColorRamp):
            return ColorRampConverter.MultiPartColorRamp_to_QgsColorRamp(ramp)
        else:
            raise NotImplementedException('Converting {} not implemented yet'.format(ramp.__class__.__name__))

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

        def fix_range(val):
            """
            Converts saturation/values range from 0-100 in esri symbols, to 0-255 for QGIS
            """
            return 255 * val / 100

        # TODO - how to correctly handle color count option?
        out = QgsLimitedRandomColorRamp(count=100,
                                        hueMax=ramp.hue_max, hueMin=ramp.hue_min,
                                        satMax=fix_range(ramp.sat_max), satMin=fix_range(ramp.sat_min),
                                        valMax=fix_range(ramp.val_max), valMin=fix_range(ramp.val_min))
        return out

    @staticmethod
    def AlgorithmicColorRamp_to_QgsColorRamp(ramp: AlgorithmicColorRamp):
        """
        Converts a AlgorithmicColorRamp to a QgsColorRamp
        """
        out = QgsGradientColorRamp(ColorConverter.color_to_qcolor(ramp.color1),
                                   ColorConverter.color_to_qcolor(ramp.color2))
        return out

    @staticmethod
    def MultiPartColorRamp_to_QgsColorRamp(ramp: MultiPartColorRamp):
        """
        Converts a MultiPartColorRamp to a QgsColorRamp
        """
        total_length = 0
        start_color = None
        end_color = None
        for i, p in enumerate(ramp.parts):
            if not isinstance(p, (AlgorithmicColorRamp, PresetColorRamp)):
                raise NotImplementedException(
                    'Converting MultiPartColorRamp with a {} part is not supported'.format(p.__class__.__name__))
            if len(ramp.part_lengths) > i:
                total_length += ramp.part_lengths[i]
            else:
                total_length += 1
            if not start_color:
                if isinstance(p, AlgorithmicColorRamp):
                    start_color = ColorConverter.color_to_qcolor(p.color1)
                elif isinstance(p, PresetColorRamp):
                    start_color = ColorConverter.color_to_qcolor(p.colors[0])
            if isinstance(p, AlgorithmicColorRamp):
                end_color = ColorConverter.color_to_qcolor(p.color2)
            elif isinstance(p, PresetColorRamp):
                end_color = ColorConverter.color_to_qcolor(p.colors[-1])

        out = QgsGradientColorRamp(start_color, end_color)
        stops = []
        current_length = 0
        for i, p in enumerate(ramp.parts[:-1]):
            if len(ramp.part_lengths) > i:
                this_length = ramp.part_lengths[i]
            else:
                this_length = 1

            if isinstance(p, PresetColorRamp):
                color_length = this_length / len(p.colors) / total_length
                for j, c in enumerate(p.colors):
                    stops.append(QgsGradientStop(current_length / total_length + color_length * j,
                                                 ColorConverter.color_to_qcolor(c)))
                    stops.append(QgsGradientStop((current_length / total_length + color_length * (j + 1)) * 0.999999,
                                                 ColorConverter.color_to_qcolor(c)))

            current_length += this_length
            current_offset = current_length / total_length
            if isinstance(p, AlgorithmicColorRamp):
                stops.append(QgsGradientStop(current_offset, ColorConverter.color_to_qcolor(p.color2)))
        out.setStops(stops)

        return out
