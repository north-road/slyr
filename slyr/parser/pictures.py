#!/usr/bin/env python

"""
Picture handling utilities
"""

import base64
import struct
from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QImage, QColor, qRgba


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

        encoded = base64.b64encode(png_data.data()).decode('UTF-8')

        return encoded

    @staticmethod
    def to_base64(data: bin) -> str:
        """
        Converts generic picture data to base 64
        """
        encoded = base64.b64encode(data).decode('UTF-8')
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
    def set_colors(data: bin, fg: QColor, bg: QColor, trans: QColor) -> bin:  # pylint: disable=too-many-locals
        """
        Burns foreground and background colors into a raster image, and returns
        the results as a PNG binary
        """
        image = QImage()
        image.loadFromData(data)

        image = image.convertToFormat(QImage.Format_ARGB32)
        ucharptr = image.bits()
        ucharptr.setsize(image.byteCount() * image.height())

        fg_rgba = qRgba(fg.red(), fg.green(), fg.blue(), fg.alpha()) if fg else None
        bg_rgba = qRgba(bg.red(), bg.green(), bg.blue(), bg.alpha()) if bg else None

        # TODO: what's this even for?
        _ = qRgba(trans.red(), trans.green(), trans.blue(), trans.alpha()) if trans else None

        for y in range(image.height()):
            start = y * image.width() * 4
            for x in range(image.width()):
                x_start = x * 4 + start
                rgba = struct.unpack('I', ucharptr[x_start:x_start + 4])[0]

                if fg_rgba is not None and rgba == 0xff000000:
                    ucharptr[x_start:x_start + 4] = struct.pack('I', fg_rgba)
                elif bg_rgba is not None and rgba == 0xffffffff:
                    ucharptr[x_start:x_start + 4] = struct.pack('I', bg_rgba)

        # convert to PNG
        png_data = QBuffer()
        image.save(png_data, "png")
        return png_data.data()

    @staticmethod
    def to_embedded_svg(data: bin) -> str:
        """
        Converts embedded image data to a PNG embedded within
        an svg.... phew!
        """
        image = QImage()
        image.loadFromData(data)
        size = image.size()

        encoded = PictureUtils.to_base64_png(data)

        return """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<image width="{}" height="{}" xlink:href="data:image/png;base64,{}"/>
</svg>""".format(size.width(), size.height(), encoded)
