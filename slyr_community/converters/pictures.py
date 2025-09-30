#!/usr/bin/env python

# /***************************************************************************
# crs.py
# ----------
# Date                 : March 2020
# copyright            : (C) 2020 by Nyall Dawson
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
Picture handling utilities
"""

import base64
import struct

from qgis.PyQt.QtCore import QBuffer
from qgis.PyQt.QtGui import QImage, QColor, qRgba, QPainter, qRed, qGreen, qBlue

from .color import ColorConverter
from ..parser.exceptions import UnreadablePictureException
from ..parser.objects.picture import StdPicture


class PictureUtils:
    """
    Picture handling utilities
    """

    @staticmethod
    def to_base64_png(data: bin) -> str:
        """
        Reads embedded image data, and converts to
        a base 64 encoded PNG
        """

        # read image from embedded file
        image = QImage()
        image.loadFromData(data)

        # convert to PNG
        png_data = QBuffer()
        image.save(png_data, "png")

        encoded = base64.b64encode(png_data.data()).decode("UTF-8")

        return encoded

    @staticmethod
    def to_base64(data: bin) -> str:
        """
        Converts generic picture data to base 64
        """
        encoded = base64.b64encode(data).decode("UTF-8")
        return encoded

    @staticmethod
    def is_emf(data: bin) -> bool:
        """
        Returns true if the data is an EMF file
        """

        # bit of a hack
        image = QImage()
        image.loadFromData(data)
        if image.isNull():
            return True

        return False

    @staticmethod
    def to_png(data: bin, path: str):
        """
        Reads embedded image data, and saves as a PNG
        """

        # read image from embedded file
        image = QImage()
        image.loadFromData(data)

        image.save(path)

    @staticmethod
    def width_pixels(data: bin) -> int:
        """
        Reads embedded image data, and saves as a PNG
        """

        # read image from embedded file
        image = QImage()
        image.loadFromData(data)
        return image.width()

    @staticmethod
    def colorize_picture(picture, color):
        """
        Applies a color overlay to a picture, emulating the ArcMap
        results
        """
        if issubclass(picture.__class__, StdPicture):
            picture = picture.picture

        if color is None or color.is_null:
            fg_color = QColor()
        else:
            fg_color = ColorConverter.color_to_qcolor(color)

        return PictureUtils.colorize_picture_data(picture.content, fg_color)

    @staticmethod
    def colorize_picture_data(data, color: QColor, fix_alpha=True):
        """
        Colorizes picture data
        """
        image = QImage()
        image.loadFromData(data)
        if image.isNull():
            raise UnreadablePictureException("Could not read embedded picture data")

        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        ucharptr = image.bits()
        try:
            ucharptr.setsize(image.sizeInBytes() * image.height())
        except AttributeError:
            ucharptr.setsize(image.byteCount() * image.height())

        # assume top left pixel is transparent?
        if fix_alpha:
            c = image.pixelColor(0, 0)
            trans_rgba = qRgba(c.red(), c.green(), c.blue(), c.alpha())
            actual_trans_rgba = qRgba(c.red(), c.green(), c.blue(), 0)

            for y in range(image.height()):
                start = y * image.width() * 4
                for x in range(image.width()):
                    x_start = x * 4 + start
                    rgba = struct.unpack("I", ucharptr[x_start : x_start + 4])[0]

                    if rgba == trans_rgba:
                        ucharptr[x_start : x_start + 4] = struct.pack(
                            "I", actual_trans_rgba
                        )

        if not color.isValid():
            return image

        alpha = image.copy()
        p = QPainter(image)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.setBrush(color)
        p.drawRect(image.rect())
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        p.drawImage(0, 0, alpha)
        p.end()
        return image

    @staticmethod
    def set_colors(data: bin, fg: QColor, bg: QColor, trans: QColor) -> bin:  # pylint: disable=too-many-locals
        """
        Burns foreground and background colors into a raster image, and returns
        the results as a PNG binary
        """
        image = QImage()
        image.loadFromData(data)
        if image.isNull():
            raise UnreadablePictureException("Could not read embedded picture data")

        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        ucharptr = image.bits()
        try:
            ucharptr.setsize(image.sizeInBytes() * image.height())
        except AttributeError:
            ucharptr.setsize(image.byteCount() * image.height())

        fg_rgba = (
            qRgba(fg.red(), fg.green(), fg.blue(), fg.alpha())
            if fg and fg.isValid()
            else None
        )
        bg_rgba = (
            qRgba(bg.red(), bg.green(), bg.blue(), bg.alpha())
            if bg and bg.isValid()
            else None
        )

        COLOR_TOLERANCE = 40

        fg_comp = 0
        bg_comp = 255

        for y in range(image.height()):
            start = y * image.width() * 4
            for x in range(image.width()):
                x_start = x * 4 + start
                rgba = struct.unpack("I", ucharptr[x_start : x_start + 4])[0]
                red = qRed(rgba)
                blue = qBlue(rgba)
                green = qGreen(rgba)

                if (
                    trans
                    and abs(red - trans.red()) < COLOR_TOLERANCE
                    and abs(green - trans.green()) < COLOR_TOLERANCE
                    and abs(blue - trans.blue()) < COLOR_TOLERANCE
                ):
                    ucharptr[x_start : x_start + 4] = struct.pack(
                        "I", qRgba(0, 0, 0, 0)
                    )
                elif (
                    fg_rgba is not None
                    and abs(red - fg_comp) < COLOR_TOLERANCE
                    and abs(green - fg_comp) < COLOR_TOLERANCE
                    and abs(blue - fg_comp) < COLOR_TOLERANCE
                ):
                    ucharptr[x_start : x_start + 4] = struct.pack("I", fg_rgba)
                elif (
                    bg_rgba is not None
                    and abs(red - bg_comp) < COLOR_TOLERANCE
                    and abs(green - bg_comp) < COLOR_TOLERANCE
                    and abs(blue - bg_comp) < COLOR_TOLERANCE
                ):
                    ucharptr[x_start : x_start + 4] = struct.pack("I", bg_rgba)

        # convert to PNG
        png_data = QBuffer()
        image.save(png_data, "png")
        return png_data.data()

    @staticmethod
    def to_embedded_svg(data: bin, fg: QColor, bg: QColor, trans: QColor) -> str:
        """
        Converts embedded image data to a PNG embedded within
        an svg.... phew!
        """

        image = QImage()
        image.loadFromData(data)
        size = image.size()

        png_data = PictureUtils.set_colors(data, fg, bg, trans)

        encoded = PictureUtils.to_base64_png(png_data)

        return """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<image width="{}" height="{}" xlink:href="data:image/png;base64,{}"/>
</svg>""".format(size.width(), size.height(), encoded)
