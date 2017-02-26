#!/usr/bin/env python

from struct import (pack,
                    unpack)
import binascii
from colormath.color_objects import (LabColor, sRGBColor)
from colormath.color_conversions import convert_color

"""
Extracts colors from a style blob
"""


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
    if binascii.hexlify(m) == '96':
        return 'rgb'
    elif binascii.hexlify(m) == '92':
        return 'hsv'
    elif binascii.hexlify(m) == '97':
        return 'cmyk'
    else:
        assert False, 'unknown color model {} at {}'.format(binascii.hexlify(m), hex(start))


def read_color(file_handle):
    try:
        l = unpack("<d", file_handle.read(8))[0]
        a = unpack("<d", file_handle.read(8))[0]
        b = unpack("<d", file_handle.read(8))[0]
        # print (l, a, b)
        # scale b from ESRI -100/100 to -128/128
        a = a * 128.0 / 100.0
        b = b * 128.0 / 100.0
        # print (l,a,b)
        dither = binascii.hexlify(file_handle.read(1)) == '01'
        is_null = binascii.hexlify(file_handle.read(1)) == 'ff'
        color = convert_color(LabColor(l, a, b, observer='2', illuminant='d65'), sRGBColor)
        return {'R': round(color.rgb_r * 255),
                'G': round(color.rgb_g * 255),
                'B': round(color.rgb_b * 255),
                'dither': dither,
                'is_null': is_null}
    except:
        return None
