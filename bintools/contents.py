#!/usr/bin/env python

"""
Tries to extract useful components from ESRI .style blobs
"""

import os
from colormath.color_objects import *
from colormath.color_conversions import convert_color
import binascii
from struct import *

# read all blobs
path = os.path.join('styles', 'fill_bin')
blobs = {}
for fn in os.listdir(path):
    file = os.path.join(path, fn)
    if os.path.isfile(file):
        with open(file, 'rb') as f:
            blobs[fn] = f.read()

# try to read in fill color from blobs
start = 0xc9
for k, v in blobs.items():
    try:
        c = v[start:start + 8]
        c2 = unpack("<d", c)[0]
        i = v[start + 8:start + 16]
        i2 = unpack("<d", i)[0]
        e = v[start + 16:start + 24]
        e2 = unpack("<d", e)[0]

        rgb = convert_color(LabColor(c2, i2, e2), sRGBColor, target_illuminant='c2')
    except:
        print('BAD read: ' + k)
        continue

    print(k, rgb.rgb_r * 255, rgb.rgb_g * 255, rgb.rgb_b * 255)
