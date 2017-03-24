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

def xyz709_to_rgb(x, y, z):
    r = 3.240479 * x -1.53715 * y -0.498535 * z
    g = -0.969256 * x + 1.875991 * y + 0.041556 * z
    b = 0.055648 * x -0.204043 * y +1.057311 * z
    return r, g, b

def cielab_to_xyz(l,a,b):
    print l,a,b
    fy = (l+16)/116.0
    fz =  fy - (b/200.0)
    fx = a/500.0 + fy
    e = 0.008856
    k = 903.3
    if fx ** 3 > e:
        xr = fx ** 3
    else:
        xr = (116*fx-16)/k
    if l > k * e:
        yr = ((l+16)/116.0)**3
    else:
        yr = l/k
    if fz ** 3 > e:
        zr = fz ** 3
    else:
        zr = (116*fz - 16)/k
    print xr,yr,zr
    return xr,yr,zr

    Xr = 0.64
    Yr = 0.33
    Zr = 0.30
    print  xr*Xr, yr * Yr, zr * Zr
    return xr*Xr, yr * Yr, zr * Zr

def cielab_to_rgb(l,a,b):
    return xyz709_to_rgb(*cielab_to_xyz(l,a,b))

def read_color(file_handle):
  #  try:
  if True:
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
        #r, g, b = cielab_to_rgb(l,a,b)
        return {'R': round(color.rgb_r * 255),
                'G': round(color.rgb_g* 255),
                'B': round(color.rgb_b * 255),
                'dither': dither,
                'is_null': is_null}
  #  except:
  #      return None
