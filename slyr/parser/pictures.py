#!/usr/bin/env python

"""
Picture handling utilities
"""

import io
import base64
from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QImage


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
