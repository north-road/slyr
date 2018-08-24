import unittest
import os
from slyr.converters.dictionary import DictionaryConverter
from slyr.parser.symbol_parser import read_symbol

expected = {
    'marker_bin':
        {
            'Arrow marker.bin':
                {
                    'skip': True,
                    'type': 'MarkerSymbol',
                    'levels': [None]
                },
            'Character marker.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'ESRI Default Marker',
                        'size': 8,
                        'angle': 0,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker arial.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'Arial',
                        'size': 8,
                        'angle': 0,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker angle 35.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'ESRI Default Marker',
                        'size': 8,
                        'angle': 35,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker angle -35.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'ESRI Default Marker',
                        'size': 8,
                        'angle': -35,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker R255 G0 B0.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'ESRI Default Marker',
                        'size': 8,
                        'angle': 0,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker size 16.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'ESRI Default Marker',
                        'size': 16,
                        'angle': 0,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker Unicode 254.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 254,
                        'font': 'ESRI Default Marker',
                        'size': 8,
                        'angle': 0,
                        'x_offset': 0,
                        'y_offset': 0
                    }
                    ]
                },
            'Character marker xoffset 7 yoffset 9.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'CharacterMarkerSymbolLayer',
                        'enabled': False,  # TODO -- not correct, should be True!
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'unicode': 34,
                        'font': 'ESRI Default Marker',
                        'size': 8,
                        'angle': 0,
                        'x_offset': 7,
                        'y_offset': 9
                    }
                    ]
                },
            'Picture marker.bin':
                {
                    'skip': True,
                    'type': 'MarkerSymbol',
                    'levels': [None]
                },
            'R255 G0 B0 circle marker size 12.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 12,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 circle marker size 12 halo size 7.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': True,
                    'halo_size': 7.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 12,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 circle marker size 12 halo size 7 fill.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': True,
                    'halo_size': 7.0,
                    'halo_symbol_type': 'FillSymbol',
                    'halo_symbol':
                        {
                            'type': 'FillSymbol',
                            'levels': [{
                                'type': 'SimpleFillSymbolLayer',
                                'enabled': True,
                                'locked': False,
                                'color_model': 'rgb',
                                'color':
                                    {
                                        'R': 255,
                                        'G': 0,
                                        'B': 0,
                                        'is_null': False,
                                        'dither': False
                                    },
                                'outline_layer': {
                                    'type': 'SimpleLineSymbolLayer',
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 3.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0,
                                            'G': 255,
                                            'B': 0,
                                            'is_null': False,
                                            'dither': True
                                        }
                                }
                            }
                            ]
                        },
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 12,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 circle marker size 8 xoffset 2.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 8,
                        'x_offset': 2,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 circle marker size 8 yoffset 3.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 3,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'Two layers.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    },
                        {
                            'type': 'SimpleMarkerSymbolLayer',
                            'enabled': False,
                            'locked': True,
                            'color_model': 'rgb',
                            'color':
                                {
                                    'R': 0,
                                    'G': 112,
                                    'B': 255,
                                    'is_null': False,
                                    'dither': False
                                },
                            'marker_type': 'circle',
                            'size': 6,
                            'x_offset': 3,
                            'y_offset': -5,
                            'outline_enabled': False,
                            'outline_color_model': 'rgb',
                            'outline_color':
                                {
                                    'R': 0,
                                    'G': 0,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': False
                                },
                            'outline_size': 1.0
                        }
                    ]
                },
            'Two layers different outline.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': True,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 255,
                                'G': 255,
                                'B': 0,
                                'is_null': False,
                                'dither': True
                            },
                        'outline_size': 1.0
                    },
                        {
                            'type': 'SimpleMarkerSymbolLayer',
                            'enabled': False,
                            'locked': True,
                            'color_model': 'rgb',
                            'color':
                                {
                                    'R': 0,
                                    'G': 112,
                                    'B': 255,
                                    'is_null': False,
                                    'dither': False
                                },
                            'marker_type': 'circle',
                            'size': 6,
                            'x_offset': 3,
                            'y_offset': -5,
                            'outline_enabled': True,
                            'outline_color_model': 'rgb',
                            'outline_color':
                                {
                                    'R': 0,
                                    'G': 255,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': True
                                },
                            'outline_size': 9.0
                        }
                    ]
                },
            'R255 G0 B0 circle marker size 8 with outline.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': True,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 circle marker size 8.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'circle',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 cross marker size 8.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'cross',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 square marker size 8.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'square',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 X diamond size 8.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'diamond',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
            'R255 G0 B0 X marker size 8.bin':
                {
                    'type': 'MarkerSymbol',
                    'halo': False,
                    'halo_size': 2.0,
                    'halo_symbol_type': 'SimpleFillSymbolLayer',
                    'levels': [{
                        'type': 'SimpleMarkerSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'marker_type': 'x',
                        'size': 8,
                        'x_offset': 0,
                        'y_offset': 0,
                        'outline_enabled': False,
                        'outline_color_model': 'rgb',
                        'outline_color':
                            {
                                'R': 0,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_size': 1.0
                    }
                    ]
                },
        },
    'fill_bin':
        {
            '3D Texture fill R255 G0 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Abandoned irrigated perennial horticulture.bin':
                {
                    'type': 'FillSymbol',
                    'levels': [{
                        'type': 'SimpleFillSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 232,
                                'G': 190,
                                'B': 255,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': 'LineSymbol',
                                'levels': [{
                                    'type': 'CartographicLineSymbolLayer',
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'color':
                                        {
                                            'R': 0,
                                            'G': 0,
                                            'B': 0,
                                            'is_null': False,
                                            'dither': False
                                        },
                                    'width': 0.5,
                                    'cap': 'square',
                                    'join': 'miter',
                                    'offset': 0.0,
                                    'pattern_interval': 0.0,
                                    'pattern_parts': []
                                }
                                ]
                            }
                    }
                    ]
                },
            'Black cm.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black CMYK.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black dither non null  no outline.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black dither null.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black HSV.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black inches.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black mm.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black null.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black outline R0 G0 B0 disabled outline.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black outline R0 G0 B0 no color.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black outline R0 G0 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Black.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Gradient fill.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Line fill.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'many layers.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Marker fill.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'Picture fill.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G0 B1 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G0 B1.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G0 B255 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G0 B255.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G1 B0 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G1 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G255 B0 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R0 G255 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R1 G0 B0 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R1 G0 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R1 G1 B1.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R2 G2 B2.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R254 G254 B254.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G0 B0 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G0 B0 HSV.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G0 B0 layer disabled.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G0 B0 locked.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G0 B0 two levels.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G0 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 dither.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dash.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dashdot.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dashdotdot.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dithered.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dot.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 null.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 width 2.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255 outline R255 G255 B255.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                },
            'R255 G255 B255.bin':
                {
                    'type': 'FillSymbol',
                    'levels': [{
                        'type': 'SimpleFillSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 255,
                                'B': 255,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_layer': {
                            'type': 'SimpleLineSymbolLayer',
                            'enabled': True,
                            'locked': False,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 240,
                                    'G': 240,
                                    'B': 240,
                                    'is_null': True,
                                    'dither': True
                                }
                        }
                    }
                    ]
                },
            'Simple fill with simple outline.bin':
                {
                    'type': 'FillSymbol',
                    'levels': [{
                        'type': 'SimpleFillSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': 'LineSymbol',
                                'levels': [{
                                    'type': 'SimpleLineSymbolLayer',
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 1.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0,
                                            'G': 255,
                                            'B': 0,
                                            'is_null': False,
                                            'dither': True
                                        }
                                }
                                ]
                            }
                    }
                    ]
                },
            'Simple fill with two layer outline.bin':
                {
                    'type': 'FillSymbol',
                    'levels': [{
                        'type': 'SimpleFillSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': 'LineSymbol',
                                'levels': [{
                                    'type': 'SimpleLineSymbolLayer',
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 1.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0,
                                            'G': 255,
                                            'B': 0,
                                            'is_null': False,
                                            'dither': True
                                        }
                                },
                                    {
                                        'type': 'SimpleLineSymbolLayer',
                                        'enabled': False,
                                        'locked': True,
                                        'color_model': 'rgb',
                                        'width': 2.0,
                                        'line_type': 'solid',
                                        'color':
                                            {
                                                'R': 0,
                                                'G': 0,
                                                'B': 255,
                                                'is_null': False,
                                                'dither': True
                                            }
                                    }
                                ]
                            }
                    }
                    ]
                },
            'Two layer with two layer outlines.bin':
                {
                    'type': 'FillSymbol',
                    'levels': [{
                        'type': 'SimpleFillSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': 'LineSymbol',
                                'levels': [{
                                    'type': 'SimpleLineSymbolLayer',
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 1.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0,
                                            'G': 255,
                                            'B': 0,
                                            'is_null': False,
                                            'dither': True
                                        }
                                },
                                    {
                                        'type': 'SimpleLineSymbolLayer',
                                        'enabled': False,
                                        'locked': True,
                                        'color_model': 'rgb',
                                        'width': 2.0,
                                        'line_type': 'solid',
                                        'color':
                                            {
                                                'R': 0,
                                                'G': 0,
                                                'B': 255,
                                                'is_null': False,
                                                'dither': True
                                            }
                                    }
                                ]
                            }
                    },
                        {
                            'type': 'SimpleFillSymbolLayer',
                            'enabled': True,
                            'locked': True,
                            'color_model': 'rgb',
                            'color':
                                {
                                    'R': 0,
                                    'G': 255,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': True
                                },
                            'outline_symbol':
                                {
                                    'type': 'LineSymbol',
                                    'levels': [{
                                        'type': 'SimpleLineSymbolLayer',
                                        'enabled': True,
                                        'locked': False,
                                        'color_model': 'rgb',
                                        'width': 2.0,
                                        'line_type': 'solid',
                                        'color':
                                            {
                                                'R': 110,
                                                'G': 110,
                                                'B': 110,
                                                'is_null': False,
                                                'dither': True
                                            }
                                    },
                                        {
                                            'type': 'SimpleLineSymbolLayer',
                                            'enabled': True,
                                            'locked': True,
                                            'color_model': 'rgb',
                                            'width': 1.0,
                                            'line_type': 'dashed',
                                            'color':
                                                {
                                                    'R': 255,
                                                    'G': 0,
                                                    'B': 0,
                                                    'is_null': False,
                                                    'dither': False
                                                }
                                        }
                                    ]
                                }
                        }
                    ]
                },
            'R255 G0 B0 with cartographic line outline.bin':
                {
                    'type': 'FillSymbol',
                    'levels': [{
                        'type': 'SimpleFillSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': 'LineSymbol',
                                'levels': [{
                                    'type': 'CartographicLineSymbolLayer',
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'color':
                                        {
                                            'R': 0,
                                            'G': 0,
                                            'B': 255,
                                            'is_null': False,
                                            'dither': True
                                        },
                                    'width': 4,
                                    'cap': 'round',
                                    'join': 'bevel',
                                    'offset': -7,
                                    'pattern_interval': 1.0,
                                    'pattern_parts': []
                                }
                                ]
                            }
                    }
                    ]
                },
            'v10_5.bin':
                {
                    'skip': True,
                    'type': 'FillSymbol',
                    'levels': [None]
                }
        },

    'line_bin':
        {
            '3d simple line symbol width 8.bin':
                {
                    'skip': True,
                    'type': 'LineSymbol',
                    'levels': [None]
                },
            '3d texture line symbol width 8.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True,
                    'levels': [None]
                },
            'Cartographic line both arrow.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True
                },
            'Cartographic line end arrow.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True
                },
            'Cartographic line start arrow.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True
                },
            'Cartographic line symbol width 8.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 8.0,
                        'cap': 'butt',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line bevel join.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'butt',
                        'join': 'bevel',
                        'offset': 0.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line offset -4.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 8.0,
                        'cap': 'butt',
                        'join': 'miter',
                        'offset': -4.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line offset 5.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 8.0,
                        'cap': 'butt',
                        'join': 'miter',
                        'offset': 5.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line round join.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'butt',
                        'join': 'round',
                        'offset': 0.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line round.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'round',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line round width 4.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 4,
                        'cap': 'round',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }]
                },
            'Cartographic line round width 4 disabled.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': False,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 4,
                        'cap': 'round',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line square.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 1.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 0.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 1.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 00.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 2.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 01.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 1.0], [1.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 10.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[1.0, 1.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 11.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[2.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 1.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[1.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 110.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[2.0, 1.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 111.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[3.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 100.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[1.0, 2.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 101.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[1.0, 1.0], [1.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 1010.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[1.0, 1.0], [1.0, 1.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 000.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 3.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 011.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 1.0], [2.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 010.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 1.0], [1.0, 1.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 001.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[0.0, 2.0], [1.0, 0.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 101001000010.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': [[1.0, 1.0], [1.0, 2.0], [1.0, 4.0], [1.0, 1.0]]
                    }
                    ]
                },
            'Cartographic line square pattern interval 7.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'CartographicLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.999921007999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0.0,
                        'pattern_interval': 7.0,
                        'pattern_parts': []
                    }
                    ]
                },
            'Dash dot dot.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dash dot dot',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            }
                    }
                    ]
                },
            'Dash dot.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dash dot',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            }
                    }
                    ]
                },
            'Dashed.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dashed',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            }
                    }
                    ]
                },
            'Dotted.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dotted',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            }
                    }
                    ]
                },
            'Hash line symbol width 8.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True,
                    'levels': [None]
                },
            'Line disabled.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': False,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'line_type': 'solid',
                        'width': 1.0
                    }
                    ]
                },
            'Line locked.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': True,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'line_type': 'solid',
                        'width': 1.0
                    }
                    ]
                },
            'Marker line symbol width 8.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True,
                    'levels': [None]
                },
            'Null.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'null',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            }
                    }
                    ]
                },
            'Picture line symbol width 8.bin':
                {
                    'type': 'LineSymbol',
                    'skip': True,
                    'levels': [None]
                },
            'Solid 1.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'solid',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            }
                    }
                    ]
                },
            'Solid 2.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [{
                        'type': 'SimpleLineSymbolLayer',
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255,
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'line_type': 'solid',
                        'width': 2.0
                    }
                    ]
                },
            'Two levels.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [
                        {
                            'type': 'SimpleLineSymbolLayer',
                            'enabled': True,
                            'locked': False,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 255,
                                    'G': 0,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': False
                                }
                        },
                        {
                            'type': 'SimpleLineSymbolLayer',
                            'enabled': True,
                            'locked': True,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 110,
                                    'G': 110,
                                    'B': 110,
                                    'is_null': False,
                                    'dither': True
                                }
                        }
                    ]
                },
            'Three levels.bin':
                {
                    'type': 'LineSymbol',
                    'levels': [
                        {
                            'type': 'SimpleLineSymbolLayer',
                            'enabled': True,
                            'locked': False,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'dotted',
                            'color':
                                {
                                    'R': 255,
                                    'G': 0,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': False
                                }
                        },
                        {
                            'type': 'SimpleLineSymbolLayer',
                            'enabled': True,
                            'locked': True,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'dash dot',
                            'color':
                                {
                                    'R': 110,
                                    'G': 110,
                                    'B': 110,
                                    'is_null': False,
                                    'dither': True
                                }
                        },
                        {
                            'type': 'SimpleLineSymbolLayer',
                            'enabled': False,
                            'locked': True,
                            'color_model': 'rgb',
                            'width': 2.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 0,
                                    'G': 255,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': True
                                }
                        }
                    ]
                }

        }
}


class TestSymbolParser(unittest.TestCase):

    def run_symbol_checks(self, path):
        # read all blobs
        blobs = []
        for fn in os.listdir(path):
            file = os.path.join(path, fn)
            if os.path.isfile(file):
                blobs.append(file)

        for file in blobs:
            print(file)
            group, symbol_name = os.path.split(file)
            path, group = os.path.split(group)

            with open(file, 'rb') as f:
                expected_symbol = expected[group][symbol_name]
                if 'skip' in expected_symbol:
                    continue
                symbol = read_symbol(f, debug=False)

                converter = DictionaryConverter()
                self.assertEqual(converter.convert_symbol(symbol), expected_symbol)

    def test_lines(self):
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'line_bin')
        self.run_symbol_checks(path)

    def test_fills(self):
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'fill_bin')
        self.run_symbol_checks(path)

    def test_markers(self):
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'marker_bin')
        self.run_symbol_checks(path)


if __name__ == '__main__':
    unittest.main()
