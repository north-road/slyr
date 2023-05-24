#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from .raster_renderer import RasterRenderer


class RasterRGBRenderer(RasterRenderer):
    """
    RasterRGBRenderer
    """

    @staticmethod
    def cls_id():
        return '577f1870-7037-11d2-9f29-00c04f8ed1d7'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.red_band = 0
        self.green_band = 0
        self.blue_band = 0
        self.red_checked = False
        self.green_checked = False
        self.blue_checked = False
        self.stretch_type = RasterRenderer.STRETCH_TYPE_NONE
        self.stretch_standard_deviations = 2.5
        self.stretch_low = 0
        self.stretch_high = 0
        self.apply_gamma = False
        self.red_gamma = 1
        self.green_gamma = 1
        self.blue_gamma = 1
        self.stats_type = RasterRenderer.STATS_DATASET
        self.invert_stretch = False
        self.display_background_value = False
        self.background_value_red = 0
        self.background_value_green = 0
        self.background_value_blue = 0
        self.background_color = None
        self.pansharpening_enabled = False
        self.pansharpening_properties = None
        self.sigmoid_strength = 1
        self.mean_parameters = None
        self.contrast_parameters = None

    @staticmethod
    def compatible_versions():
        return [4, 5, 9, 10]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)

        def handler(ref, size):
            if ref == 1:
                assert size == 4
                self.red_band = stream.read_int('red band') + 1
            elif ref == 2:
                assert size == 4
                self.green_band = stream.read_int('green band') + 1
            elif ref == 3:
                assert size == 4
                self.blue_band = stream.read_int('blue band') + 1
            elif ref == 4:
                # this looks like per-channel palettes
                stream.read(size)
            elif ref == 5:
                # bit wise or of 1 = red, 2 = green, 4 = blue, (Alpha is somewhere else??)
                assert size == 1
                res = stream.read_uchar('band visibility')
                self.red_checked = bool(res & 1)
                self.green_checked = bool(res & 2)
                self.blue_checked = bool(res & 4)
            elif ref == 6:
                assert size == 4
                self.stretch_type = stream.read_int('stretch type')
            elif ref == 7:
                assert size == 8
                self.stretch_standard_deviations = stream.read_double('stretch standard deviations')
            elif ref == 8:
                assert size == 4
                self.invert_stretch = stream.read_int('invert stretch') != 0
            elif ref == 9:
                assert size == 4
                self.display_background_value = stream.read_int('display background value') != 0
            elif ref == 10:
                assert size == 32
                self.background_value_red = stream.read_double('background value red')
                self.background_value_green = stream.read_double('background value green')
                self.background_value_blue = stream.read_double('background value blue')
                stream.read_double('unknown')
                # 0, 5547788.905079776, 5.107479463978793e-125, 1284671.038936868, 3.847363780084635e+206, 3.543732972913e-312, 1.357619704074e-311, 1.390673814061804e-309, 1.9931184764275422e+40))
            elif ref == 11:
                # a variant???
                stream.read(size)
            elif ref == 12:
                assert size == 0xffffffff
                self.background_color = stream.read_object('background color', allow_reference=False)
            elif ref == 13:
                assert size == 4
                self.stats_type = stream.read_int('stats type')
            elif ref == 14:
                assert size == 0xffffffff
                stream.read_object('red histogram', allow_reference=False)
            elif ref == 15:
                assert size == 0xffffffff
                stream.read_object('green histogram', allow_reference=False)
            elif ref == 16:
                assert size == 0xffffffff
                stream.read_object('blue histogram', allow_reference=False)
            elif ref == 17:
                assert size == 4
                self.pansharpening_enabled = stream.read_int('pansharpening enabled') != 0
            elif ref == 18:
                assert size == 0xffffffff
                self.pansharpening_properties = stream.read_object('pansharpening properties', allow_reference=False)
            elif ref == 19:
                assert size == 4
                self.apply_gamma = stream.read_int('apply gamma') != 0
            elif ref == 20:
                assert size == 24
                self.red_gamma = stream.read_double('red gamma')
                self.green_gamma = stream.read_double('green gamma')
                self.blue_gamma = stream.read_double('blue gamma')
            elif ref == 21:
                assert size == 8
                self.stretch_low = stream.read_double('stretch low')
            elif ref == 22:
                assert size == 8
                self.stretch_high = stream.read_double('stretch high')
            else:
                assert False, 'Unknown property ref {}'.format(ref)

        stream.read_indexed_properties(handler)

        if version > 5:
            stream.read_ushort('unknown flag', expected=0)
            stream.read_object('unknown color components')
            stream.read_object('unknown color components')

            self.mean_parameters = stream.read_object('mean parameters')
            self.contrast_parameters = stream.read_object('contrast parameters')

        if version > 9:
            self.sigmoid_strength = stream.read_int('sigmoid strength') + 1

        if version > 5:
            stream.read_ushort('unknown flag', expected=65535)
            stream.read_ushort('unknown flag', expected=65535)

        stream.read_ushort('unknown flag', expected=65535)
        stream.read_ushort('unknown flag', expected=65535)

        super().read(stream)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['red_band'] = self.red_band
        res['green_band'] = self.green_band
        res['blue_band'] = self.blue_band
        res['red_checked'] = self.red_checked
        res['green_checked'] = self.green_checked
        res['blue_checked'] = self.blue_checked
        res['stretch_type'] = RasterRenderer.stretch_type_to_string(self.stretch_type)
        res['stretch_standard_deviations'] = self.stretch_standard_deviations
        res['stretch_low'] = self.stretch_low
        res['stretch_high'] = self.stretch_high
        res['apply_gamma'] = self.apply_gamma
        res['red_gamma'] = self.red_gamma
        res['green_gamma'] = self.green_gamma
        res['blue_gamma'] = self.blue_gamma
        res['stats_type'] = RasterRenderer.stats_type_to_string(self.stats_type)
        res['invert_stretch'] = self.invert_stretch
        res['display_background_value'] = self.display_background_value
        res['background_value_red'] = self.background_value_red
        res['background_value_green'] = self.background_value_green
        res['background_value_blue'] = self.background_value_blue
        res['background_color'] = self.background_color.to_dict() if self.background_color else None
        res['pansharpening_enabled'] = self.pansharpening_enabled
        res[
            'pansharpening_properties'] = self.pansharpening_properties.to_dict() if self.pansharpening_properties else None
        res['sigmoid_strength'] = self.sigmoid_strength
        res['mean_parameters'] = self.mean_parameters.to_dict() if self.mean_parameters else None
        res['contrast_parameters'] = self.contrast_parameters.to_dict() if self.contrast_parameters else None
        return res


class RasterRgbRendererColorComponents(Object):
    """
    RasterRgbRendererColorComponents
    """

    @staticmethod
    def cls_id():
        return '60c06ca7-e09e-11d2-9f7b-00c04f8ece27'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.components = []

    def read(self, stream: Stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.components.append(stream.read_double('component {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'components': self.components
        }


class RasterRgbPanSharpeningProperties(Object):
    """
    RasterRgbPanSharpeningProperties
    """

    TYPE_IHS = 0
    TYPE_BROVEY = 1
    TYPE_ESRI = 2
    TYPE_MEAN = 3
    TYPE_GRAMSCHMIDT = 4

    @staticmethod
    def cls_id():
        return 'b58b1271-e6fb-4b27-8417-2b8d62d654b0'

    @staticmethod
    def pansharpen_type_to_string(pansharpen):
        if pansharpen == RasterRgbPanSharpeningProperties.TYPE_IHS:
            return 'ihs'
        elif pansharpen == RasterRgbPanSharpeningProperties.TYPE_BROVEY:
            return 'brovey'
        elif pansharpen == RasterRgbPanSharpeningProperties.TYPE_ESRI:
            return 'esri'
        elif pansharpen == RasterRgbPanSharpeningProperties.TYPE_MEAN:
            return 'mean'
        elif pansharpen == RasterRgbPanSharpeningProperties.TYPE_GRAMSCHMIDT:
            return 'gramschmidt'

        return None

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.source = None
        self.transform = None
        self.extent = None
        self.pansharpen_type = RasterRgbPanSharpeningProperties.TYPE_IHS
        self.red_weight = 0
        self.green_weight = 0
        self.blue_weight = 0
        self.ir_weight = 0

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)

        self.source = stream.read_object('source raster')

        band_count = stream.read_int('band count')
        for i in range(band_count):
            stream.read_string('band name {}'.format(i + 1))

        self.transform = stream.read_object('transform')
        self.extent = stream.read_object('envelope')

        res = stream.read_object('unknown raster dataset name')
        if res:
            band_count = stream.read_int('band count')
            for i in range(band_count):
                stream.read_string('band name {}'.format(i + 1))
            stream.read_object('unknown transform')
            stream.read_object('unknown envelope')

        self.pansharpen_type = stream.read_int('pansharpen type')

        self.red_weight = stream.read_double('red weight')
        self.green_weight = stream.read_double('green weight')
        self.blue_weight = stream.read_double('blue weight')
        self.ir_weight = stream.read_double('IR weight')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'source': self.source.to_dict() if self.source else None,
            'transform': self.transform.to_dict() if self.transform else None,
            'extent': self.extent.to_dict() if self.extent else None,
            'pansharpen_type': RasterRgbPanSharpeningProperties.pansharpen_type_to_string(self.pansharpen_type),
            'red_weight': self.red_weight,
            'green_weight': self.green_weight,
            'blue_weight': self.blue_weight,
            'ir_weight': self.ir_weight
        }
