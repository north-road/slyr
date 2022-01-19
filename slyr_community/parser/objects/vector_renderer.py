#!/usr/bin/env python
"""
Common base class for vector renderers
"""

from ..object import Object
from ..stream import Stream


class VectorRendererBase(Object):
    """
    Vector Renderer base class
    """

    ROTATE_SYMBOL_GEOGRAPHIC = 0
    ROTATE_SYMBOL_ARITHMETIC = 1

    ROTATE_FLAG_3D_NONE = 0
    ROTATE_FLAG_3D_EXPRESSION_X = 1
    ROTATE_FLAG_3D_EXPRESSION_Y = 2
    ROTATE_FLAG_3D_EXPRESSION_Z = 4
    ROTATE_FLAG_3D_RANDOM_X = 8
    ROTATE_FLAG_3D_RANDOM_Y = 16
    ROTATE_FLAG_3D_RANDOM_Z = 32

    SIZE_NONE = 0
    SIZE_RANDOM = 2
    SIZE_EXPRESSION = 1

    NORMALIZE_BY_FIELD = 0
    NORMALIZE_BY_LOG = 1
    NORMALIZE_BY_PERCENT_OF_TOTAL = 2
    NORMALIZE_BY_AREA = 3
    NORMALIZE_BY_NOTHING = 4

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.rotation_attribute = ''
        self.rotation_type = VectorRendererBase.ROTATE_SYMBOL_GEOGRAPHIC
        self.transparency_attribute = ''
        self.random_rotation_min_x = 0.0
        self.random_rotation_min_y = 0.0
        self.random_rotation_min_z = 0.0
        self.random_rotation_max_x = 360
        self.random_rotation_max_y = 360
        self.random_rotation_max_z = 360
        self.graduated_expression = ''
        self.graduated_size_type = VectorRendererBase.SIZE_NONE
        self.random_size_min = 0.1
        self.random_size_max = 100.0
        self.rotate_flag_3d = VectorRendererBase.ROTATE_FLAG_3D_NONE
        self.rotation_expression_x = ''
        self.rotation_expression_y = ''
        self.rotation_expression_z = ''

    @staticmethod
    def size_renderer_to_string(renderer):
        """
        Converts size renderer enum to a string
        """
        if renderer == VectorRendererBase.SIZE_EXPRESSION:
            return 'expression'
        elif renderer == VectorRendererBase.SIZE_NONE:
            return ''
        elif renderer == VectorRendererBase.SIZE_RANDOM:
            return 'random'
        return None

    @staticmethod
    def rotation_type_to_string(rotation_type):
        """
        Converts rotation type enum to a string
        """
        if rotation_type == VectorRendererBase.ROTATE_SYMBOL_ARITHMETIC:
            return 'arithmetic'
        elif rotation_type == VectorRendererBase.ROTATE_SYMBOL_GEOGRAPHIC:
            return 'geographic'
        return None

    @staticmethod
    def rotation_flag_to_string(flag):  # pylint: disable=too-many-return-statements
        """
        Converts rotation flag to a string
        """
        if flag == VectorRendererBase.ROTATE_FLAG_3D_NONE:
            return 'none'
        elif flag == VectorRendererBase.ROTATE_FLAG_3D_EXPRESSION_X:
            return 'expression_x'
        elif flag == VectorRendererBase.ROTATE_FLAG_3D_EXPRESSION_Y:
            return 'expression_y'
        elif flag == VectorRendererBase.ROTATE_FLAG_3D_EXPRESSION_Z:
            return 'expression_z'
        elif flag == VectorRendererBase.ROTATE_FLAG_3D_RANDOM_X:
            return 'random_x'
        elif flag == VectorRendererBase.ROTATE_FLAG_3D_RANDOM_Y:
            return 'random_y'
        elif flag == VectorRendererBase.ROTATE_FLAG_3D_RANDOM_Z:
            return 'random_z'
        return None

    @staticmethod
    def normalize_method_to_string(method):
        if method == VectorRendererBase.NORMALIZE_BY_FIELD:
            return 'normalize_by_field'
        elif method == VectorRendererBase.NORMALIZE_BY_LOG:
            return 'normalize_by_log'
        elif method == VectorRendererBase.NORMALIZE_BY_PERCENT_OF_TOTAL:
            return 'normalize_by_percent_of_total'
        elif method == VectorRendererBase.NORMALIZE_BY_AREA:
            return 'normalize_by_area'
        elif method == VectorRendererBase.NORMALIZE_BY_NOTHING:
            return 'normalize_by_nothing'
        return None

    def read_irotation_renderer2_properties(self, stream: Stream):
        """
        Read IRotationRenderer2 interface
        """
        stream.read_ushort('unknown', expected=(0, 1))
        self.rotate_flag_3d = stream.read_int('rotate flag 3d')
        stream.read_int('3d z rotation type')  # redundant
        self.rotation_expression_x = stream.read_string('rotation expression x')
        self.rotation_expression_y = stream.read_string('rotation expression y')
        self.rotation_expression_z = stream.read_string('rotation expression z')
        self.random_rotation_min_x = stream.read_double('random rotation x min')
        self.random_rotation_min_y = stream.read_double('random rotation y min')
        self.random_rotation_min_z = stream.read_double('random rotation z min')
        self.random_rotation_max_x = stream.read_double('random rotation x max')
        self.random_rotation_max_y = stream.read_double('random rotation y max')
        self.random_rotation_max_z = stream.read_double('random rotation z max')

    def read_graduated_size_properties(self, stream: Stream):
        stream.read_ushort('unknown', expected=1)
        self.graduated_size_type = stream.read_int('graduated size')
        self.graduated_expression = stream.read_string('graduated expression')
        self.random_size_min = stream.read_double('random size min')
        self.random_size_max = stream.read_double('random size max')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'rotation_attribute': self.rotation_attribute,
            'rotation_type': VectorRendererBase.rotation_type_to_string(self.rotation_type),
            'rotate_flag_3d': VectorRendererBase.rotation_flag_to_string(self.rotate_flag_3d),
            'rotation_expression_x': self.rotation_expression_x,
            'rotation_expression_y': self.rotation_expression_y,
            'rotation_expression_z': self.rotation_expression_z,
            'transparency_attribute': self.transparency_attribute,
            'random_rotation_min_x': self.random_rotation_min_x,
            'random_rotation_max_x': self.random_rotation_max_x,
            'random_rotation_min_y': self.random_rotation_min_y,
            'random_rotation_max_y': self.random_rotation_max_y,
            'random_rotation_min_z': self.random_rotation_min_z,
            'random_rotation_max_z': self.random_rotation_max_z,
            'graduated_expression': self.graduated_expression,
            'graduated_size_type': VectorRendererBase.size_renderer_to_string(self.graduated_size_type),
            'random_size_min': self.random_size_min,
            'random_size_max': self.random_size_max
        }
