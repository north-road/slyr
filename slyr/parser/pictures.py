#!/usr/bin/env python

"""
Picture handling utilities
"""

import io
import base64
from PIL import Image


class PictureUtils:
    """
    Picture handling utilities
    """

    @staticmethod
    def to_base64_png(data: bin):
        """
        Reads embedded image data, and converts to
        a base 64 encoded PNG
        """

        # read image from embedded file
        img = Image.open(io.BytesIO(data))

        # convert to PNG
        png_data = io.BytesIO()
        img.save(png_data, format="png")

        encoded = base64.b64encode(png_data.getvalue())

        return encoded
