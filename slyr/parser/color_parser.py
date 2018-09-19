#!/usr/bin/env python

from struct import (pack,
                    unpack)
import binascii
from slyr.parser.color_lut import COLOR_LUT

"""
Extracts colors from a style blob
"""


class InvalidColorException(Exception):
    pass


def read_double(file_handle):
    buffer = file_handle.read(8)
    buffer = [ord(b) for b in buffer]
    lo = buffer[0] | buffer[1] << 8 | buffer[2] << 16 | buffer[3] << 24
    hi = buffer[4] | buffer[5] << 8 | buffer[6] << 16 | buffer[7] << 24

    tmpBuffer = hi << 32 | lo
    return unpack('d', pack('Q', tmpBuffer))[0]


def read_color_model(file_handle):
    start = file_handle.tell()
    m = file_handle.read(1)
    if binascii.hexlify(m) == b'96':
        return 'rgb'
    elif binascii.hexlify(m) == b'92':
        return 'hsv'
    elif binascii.hexlify(m) == b'93':
        return 'rgb'  # technically "named" colors, but internally treated as RGB
    elif binascii.hexlify(m) == b'95':
        return 'rgb'  # technically "gray" colors, but internally treated as RGB
    elif binascii.hexlify(m) == b'97':
        return 'cmyk'
    else:
        raise InvalidColorException('unknown color model {} at {}'.format(
            binascii.hexlify(m), hex(start)))


def xyz_to_rgb(x, y, z):
    """Translate XYZ color to RGB. See http://www.brucelindbloom.com/"""

    # Transformation for AppleRGB Working Space
    r = 2.9515373 * x - 1.2894116 * y - 0.4738445 * z
    g = -1.0851093 * x + 1.9908566 * y + 0.0372026 * z
    b = 0.0854934 * x - 0.2694964 * y + 1.0912975 * z

    return r, g, b


def apply_gamma(r, g, b):
    """Apply gamma conversion"""

    # Convert to zero negative values
    if r < 0:
        r = 0
    if g < 0:
        g = 0
    if b < 0:
        b = 0

    # Gamma companding 1.8
    r = r ** (1 / 1.8)
    g = g ** (1 / 1.8)
    b = b ** (1 / 1.8)

    return r, g, b


def cielab_to_xyz(l, a, b):
    """Translate lab color to xyz. See http://www.brucelindbloom.com/"""

    fy = (l + 16) / 116.0
    fz = fy - (b / 200.0)
    fx = a / 500.0 + fy
    e = 0.008856
    k = 903.3
    if fx ** 3 > e:
        xr = fx ** 3
    else:
        xr = (116 * fx - 16) / k
    if l > k * e:
        yr = ((l + 16) / 116.0) ** 3
    else:
        yr = l / k
    if fz ** 3 > e:
        zr = fz ** 3
    else:
        zr = (116 * fz - 16) / k

    # Reference white D65

    # While 0.95047 is commonly used here, the actual REC709 standard
    # has a white point of xw = 0.3127, yw = 0.3290 (see https://en.wikipedia.org/wiki/Rec._709)
    # scaling this to the equivalent Yr of 1.0, we get an
    # Xr value of 0.3127 * 1 / 0.329 = 0.9504559270516716
    # and yes, this small variation does give a real difference in the
    # accuracy of the converted colors!!
    Xr = 0.9504559270516716
    Yr = 1.00000
    # Scaling the standard value of 1.08883 to use the rec 709 white point
    # gives 1.08883 * 0.95047 * yw / xw = 1.0888461217873364
    Zr = 1.0888461217873364

    return xr * Xr, yr * Yr, zr * Zr


def scale_and_round(r, g, b):
    """Scale to 0-255 and round valued. The algorithm seems to be extremely
    precise and equivalent to what is done inside Esri apps, except for
    very small rgb values. Often the algorithm returns 1 or 2 instead of
    the expected 0 (on a 0-255 scale).
    I think that is more likely that small values are intended to be zero,
    so I correct them"""

    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)

    if r < 5:
        r = 0
    if g < 5:
        g = 0
    if b < 5:
        b = 0

    return r, g, b


def round_lab(l, a, b):
    def round_val(v):
        return round(v * 10000) / 10000.0

    return round_val(l), round_val(a), round_val(b)


def lookup_lab(l, a, b):
    """
    Attempts to lookup an ESRI CIELAB in the manual lookup conversion table.
    This table contains overrides for which the standard LAB->XYZ->RGB conversion
    formula results in a color difference of more than 1 unit in the red, green
    or blue component when compared to ESRI's internal CIELAB -> RGB conversion.
    """
    lut_l, lut_a, lut_b = round_lab(l, a, b)
    if (lut_l, lut_a, lut_b) in COLOR_LUT:
        (r, g, b) = COLOR_LUT[(lut_l, lut_a, lut_b)]
        return r, g, b

    return None


def cielab_to_rgb(l, a, b):
    """
    Converts an ESRI CIELAB value to a RGB value
    """
    lut_result = lookup_lab(l, a, b)
    if lut_result is not None:
        return lut_result

    # lab value not present in lookup table, use standard conversion formula
    return scale_and_round(*apply_gamma(*xyz_to_rgb(*cielab_to_xyz(l, a, b))))


def read_color(file_handle, model='rgb'):
    if model == 'cmyk':
        # CMYK is nice and easy - it's just direct char representations of the C/M/Y/K integer components!
        c = unpack("B", file_handle.read(1))[0]
        m = unpack("B", file_handle.read(1))[0]
        y = unpack("B", file_handle.read(1))[0]
        k = unpack("B", file_handle.read(1))[0]
        file_handle.read(2)
        return {'C': c, 'M': m, 'Y': y, 'K': k}

    lab_l = unpack("<d", file_handle.read(8))[0]
    lab_a = unpack("<d", file_handle.read(8))[0]
    lab_b = unpack("<d", file_handle.read(8))[0]

    dither = binascii.hexlify(file_handle.read(1)) == b'01'
    is_null = binascii.hexlify(file_handle.read(1)) == b'ff'

    try:
        r, g, b = cielab_to_rgb(lab_l, lab_a, lab_b)
    except OverflowError:
        raise InvalidColorException()

    if r > 255 or r < 0 or b > 255 or b < 0 or g > 255 or g < 0:
        raise InvalidColorException()

    return {'R': r,
            'G': g,
            'B': b,
            'dither': dither,
            'is_null': is_null}


def read_magic_2(handle, color_model, debug=False):
    """
    Consumes an expected magic sequence (2), of unknown purpose
    """
    magic_2 = binascii.hexlify(handle.read(15))
    if magic_2 != b'c4e97e23d1d0118383080009b996cc':
        raise InvalidColorException('Differing magic string 2: {}'.format(magic_2))

    if color_model == 'rgb':
        if debug:
            print('Skipping some bytes at {}'.format(hex(handle.tell())))

        terminator = binascii.hexlify(handle.read(2))
        if not terminator == b'0100':
            # .lyr files have an extra 4 bytes in here - of unknown purpose
            handle.read(4)

        start = handle.tell()
        terminator = binascii.hexlify(handle.read(1))
        if terminator != b'01':
            if debug:
                print('Expected 01 at {}, got {}'.format(hex(start), terminator))

            raise InvalidColorException('Expected 01 at {}, got {}'.format(hex(start), terminator))

        # another two unknown bytes
        handle.read(2)
    elif color_model == 'hsv':
        if debug:
            print('Skipping 5 bytes at {}'.format(hex(handle.tell())))

        handle.read(5)
    elif color_model == 'cmyk':
        if debug:
            print('Skipping 4 bytes at {}'.format(hex(handle.tell())))

        handle.read(4)

    if debug:
        print('finished magic 2 at {}'.format(hex(handle.tell())))


def read_color_and_model(handle, debug=False):
    """
    Reads both the color model and the color itself from a file handle
    :return: color model, color
    """

    start = handle.tell()
    color_model = read_color_model(handle)
    if debug:
        print('Read color model ({}) at {}'.format(color_model, hex(start)))

    read_magic_2(handle, color_model, debug)

    start = handle.tell()
    color = read_color(handle, color_model)
    if debug:
        print('Read color ({}) at {} {}'.format(color_model, hex(start), color))

    return color_model, color
