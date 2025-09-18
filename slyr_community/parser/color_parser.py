#!/usr/bin/env python
"""
Extracts colors from a persistent stream binary
"""

from .color_lut import COLOR_LUT


def xyz_to_rgb(x, y, z):
    """Translate XYZ color to RGB. See http://www.brucelindbloom.com/"""

    # Transformation for AppleRGB Working Space
    r = 2.9515373 * x - 1.2894116 * y - 0.4738445 * z
    g = -1.0851093 * x + 1.9908566 * y + 0.0372026 * z
    b = 0.0854934 * x - 0.2694964 * y + 1.0912975 * z

    return r, g, b


def apply_gamma(r, g, b):
    """Apply gamma conversion"""

    # Convert to negative values to zero
    r = max(r, 0)
    g = max(g, 0)
    b = max(b, 0)

    # Gamma companding 1.8
    r = r ** (1 / 1.8)
    g = g ** (1 / 1.8)
    b = b ** (1 / 1.8)

    return r, g, b


def cielab_to_xyz(l_value, a, b):
    """Translate lab color to xyz. See http://www.brucelindbloom.com/"""

    fy = (l_value + 16) / 116.0
    fz = fy - (b / 200.0)
    fx = a / 500.0 + fy
    e = 0.008856
    k = 903.3
    if fx**3 > e:
        xr = fx**3
    else:
        xr = (116 * fx - 16) / k
    if l_value > k * e:
        yr = ((l_value + 16) / 116.0) ** 3
    else:
        yr = l_value / k
    if fz**3 > e:
        zr = fz**3
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


def round_lab(l_value, a, b):
    """
    Rounds l/a/b values
    """

    def round_val(v):
        """
        Round a lab color component
        """
        return round(v * 10000) / 10000.0

    return round_val(l_value), round_val(a), round_val(b)


def lookup_lab(l_value, a, b):
    """
    Attempts to lookup an ESRI CIELAB in the manual lookup conversion table.
    This table contains overrides for which the standard LAB->XYZ->RGB conversion
    formula results in a color difference of more than 1 unit in the red, green
    or blue component when compared to ESRI's internal CIELAB -> RGB conversion.
    """
    lut_l, lut_a, lut_b = round_lab(l_value, a, b)
    if (lut_l, lut_a, lut_b) in COLOR_LUT:
        (r, g, b) = COLOR_LUT[(lut_l, lut_a, lut_b)]
        return r, g, b

    return None


def cielab_to_rgb(l_value, a, b):
    """
    Converts an ESRI CIELAB value to a RGB value
    """
    lut_result = lookup_lab(l_value, a, b)
    if lut_result is not None:
        return lut_result

    # lab value not present in lookup table, use standard conversion formula
    return scale_and_round(*apply_gamma(*xyz_to_rgb(*cielab_to_xyz(l_value, a, b))))
