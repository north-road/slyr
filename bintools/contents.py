#!/usr/bin/env python

import os
from itertools import groupby
from colormath.color_objects import *
from colormath.color_conversions import convert_color
from struct import *

if True:
    path = 'D:/dev/style_spec/styles/fill_bin'
    bin={}
    for fn in os.listdir(path):
        file = os.path.join(path,fn)
        if os.path.isfile(file):
            with open(file,'rb') as f:
                bin[fn] = f.read()

    #with open('d:/export/styles3.csv','w') as o:
    start =0xc9
    for k,v in bin.items():
       # print (k)
        try:
            c=v[start :start +8]
            c2=unpack("<d", c)[0]
            i=v[start +8:start +16]
            i2 = unpack("<d", i)[0]
            e = v[start  + 16:start  + 24]
            e2 = unpack("<d", e)[0]
            #print (c2,i2,e2)
            rgb = convert_color(LabColor(c2, i2, e2), sRGBColor, target_illuminant='c2')
        except:
            continue


        #o.write('"' +k +'",'+str(int(rgb.rgb_r*255) )+',' +str(int( rgb.rgb_g * 255) )+',' + str(int( rgb.rgb_b *255 ) ) +'\n')

        print(k,rgb.rgb_r * 255,rgb.rgb_g * 255, rgb.rgb_b *255)
import binascii

#for k, v in bin.iteritems():
 #   print binascii.hexlify(v[124:124+8])
c={}

c[(0,0,0)] =      0x000000000000000000000000000000000000000000000000
c[(1,1,1)] =      0xBF0E01554E8BA53F00000000000000000000000000000000
c[(2,2,2)] =      0x28669E4C5AC1C23F00000000000000000000000000000000
c[(254,254,254)]= 0x8026349E84EE584000000000000000000000000000000000
c[(255,255,255)]= 0x00000000000059400000000000000000000000000000193D
c[(1,0,0)] =      0x77AD31D28614853FAC4E7111AF220640D52D4FEF829A0340
c[(0,1,0)] =      0x8B4660320FF59C3F5148F95093550AC032ACE29C3D4A0540
c[(0,0,1)] =      0xCE01487450BA6C3F281E4AB53579044013312C6B12540DC0
c[(255,0,0)] =    0xE01C58AC04464C40091768519039534082A2B8D49E065140
c[(0,255,0)] =    0x46F3DD4DDA665540BAD424C91DDF56C05E7592BA947D5240
c[(0,0,255)]=     0xD84DBD3AA1554140BF17BD2D09C85140F9DB813DD37859C0

if False:
    for k, v in c.items():
        print(k)
        start=0
        v=  binascii.unhexlify(str(v))
        #try:
        c = v[start:start + 8]
        c2 = unpack("<d", c)[0]
        i = v[start + 8:start + 16]
        i2 = unpack("<d", i)[0]
        e = v[start + 16:start + 24]
        e2 = unpack("<d", e)[0]
        rgb = convert_color(LabColor(c2, i2, e2), sRGBColor)
   # except:
   #     continue

   # o.write('"' + k + '",' + str(int(rgb.rgb_r * 255)) + ',' + str(int(rgb.rgb_g * 255)) + ',' + str(
    #    int(rgb.rgb_b * 255)) + '\n')

    print(k, rgb.rgb_r * 255, rgb.rgb_g * 255, rgb.rgb_b * 255)

def rgb2lab ( inputColor ) :

   num = 0
   RGB = [0, 0, 0]

   for value in inputColor :
       value = float(value) / 255

       if value > 0.04045 :
           value = ( ( value + 0.055 ) / 1.055 ) ** 2.4
       else :
           value = value / 12.92

       RGB[num] = value * 100
       num = num + 1

   XYZ = [0, 0, 0,]

   X = RGB [0] * 0.4124 + RGB [1] * 0.3576 + RGB [2] * 0.1805
   Y = RGB [0] * 0.2126 + RGB [1] * 0.7152 + RGB [2] * 0.0722
   Z = RGB [0] * 0.0193 + RGB [1] * 0.1192 + RGB [2] * 0.9505
   XYZ[ 0 ] = round( X, 4 )
   XYZ[ 1 ] = round( Y, 4 )
   XYZ[ 2 ] = round( Z, 4 )

   XYZ[ 0 ] = float( XYZ[ 0 ] ) / 95.047         # ref_X =  95.047   Observer= 2°, Illuminant= D65
   XYZ[ 1 ] = float( XYZ[ 1 ] ) / 100.0          # ref_Y = 100.000
   XYZ[ 2 ] = float( XYZ[ 2 ] ) / 108.883        # ref_Z = 108.883

   num = 0
   for value in XYZ :

       if value > 0.008856 :
           value = value ** ( 0.3333333333333333 )
       else :
           value = ( 7.787 * value ) + ( 16 / 116 )

       XYZ[num] = value
       num = num + 1

   Lab = [0, 0, 0]

   L = (116 * XYZ[1]) - 16
   a = 500 * (XYZ[0] - XYZ[1])
   b = 200 * (XYZ[1] - XYZ[2])

   Lab[0] = round(L, 4)
   Lab[1] = round(a, 4)
   Lab[2] = round(b, 4)

   return Lab


if False:
    h = c[(255,255,255)]
    for i in range(24*8):
        masked = h & i
        if masked >> i == 255:
            print(i)
            print(hex(masked))

    print(hex(h << 6))
    #print (lngRGB >> 1) & 0x100
    #print()
    #print (lngRGB / 0x100) % 0x100
    #print (lngRGB / 0x10000) % 0x100

def diff():
    k1=bin.keys()[0]
    f1=bin[k1]

    for b2 in range(1,len(bin)):
        f2 = bin[bin.keys()[b2]]
        matches = []
        for k, g in groupby(range(min(len(f1), len(f2))), key=lambda i: f1[i] == f2[i]):
            if k:
                pos = next(g)
                length = len(list(g)) + 1
                matches.append((pos, length))
           
        print(matches)
