import unittest
import os
from symbol_parser import (read_symbol,
                           LineSymbol,
                           FillSymbol,
                           SimpleLineSymbolLayer,
                           CartographicLineSymbolLayer,
                           SimpleFillSymbolLayer)

expected = {
    'fill_bin':
        {
            '3D Texture fill R255 G0 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Abandoned irrigated perennial horticulture.bin':
                {
                    'type': FillSymbol,
                    'levels': [{
                        'type': SimpleFillSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 245.0,  # should be 232
                                'G': 200.0,  # should be 190
                                'B': 264.0,  # should be 255
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': LineSymbol,
                                'levels': [{
                                    'type': CartographicLineSymbolLayer,
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'color':
                                        {
                                            'R': 0.0,
                                            'G': 0.0,
                                            'B': 0.0,
                                            'is_null': False,
                                            'dither': False
                                        },
                                    'width': 0.5,
                                    'cap': 'square',
                                    'join': 'miter',
                                    'offset': 0.0,
                                    'pattern_interval': 0.0
                                }
                                ]
                            }
                    }
                    ]
                },
            'Black cm.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black CMYK.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black dither non null  no outline.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black dither null.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black HSV.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black inches.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black mm.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black null.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black outline R0 G0 B0 disabled outline.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black outline R0 G0 B0 no color.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black outline R0 G0 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Black.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Gradient fill.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Line fill.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'many layers.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Marker fill.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'Picture fill.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G0 B1 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G0 B1.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G0 B255 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G0 B255.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G1 B0 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G1 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G255 B0 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R0 G255 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R1 G0 B0 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R1 G0 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R1 G1 B1.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R2 G2 B2.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R254 G254 B254.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G0 B0 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G0 B0 HSV.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G0 B0 layer disabled.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G0 B0 locked.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G0 B0 two levels.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G0 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 dither.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dash.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dashdot.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dashdotdot.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dithered.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 dot.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 null.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0 width 2.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R0 G0 B0.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255 outline R255 G255 B255.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                },
            'R255 G255 B255.bin':
                {
                    'type': FillSymbol,
                    'levels': [{
                        'type': SimpleFillSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 255.0,
                                'G': 255.0,
                                'B': 255.0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_layer': {
                            'type': SimpleLineSymbolLayer,
                            'enabled': True,
                            'locked': False,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 243.0,  # should be 240
                                    'G': 243,  # should be 240
                                    'B': 243,  # should be 240
                                    'is_null': True,
                                    'dither': True
                                }
                        }
                    }
                    ]
                },
            'Simple fill with simple outline.bin':
                {
                    'type': FillSymbol,
                    'levels': [{
                        'type': SimpleFillSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0.0,
                                'B': 0.0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': LineSymbol,
                                'levels': [{
                                    'type': SimpleLineSymbolLayer,
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 1.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0.0,
                                            'G': 257.0,  # should be 255
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
                    'type': FillSymbol,
                    'levels': [{
                        'type': SimpleFillSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0.0,
                                'B': 0.0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': LineSymbol,
                                'levels': [{
                                    'type': SimpleLineSymbolLayer,
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 1.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0.0,
                                            'G': 257.0,  # should be 255
                                            'B': 0,
                                            'is_null': False,
                                            'dither': True
                                        }
                                },
                                    {
                                        'type': SimpleLineSymbolLayer,
                                        'enabled': False,
                                        'locked': True,
                                        'color_model': 'rgb',
                                        'width': 2.0,
                                        'line_type': 'solid',
                                        'color':
                                            {
                                                'R': 0.0,
                                                'G': 0.0,
                                                'B': 303.0,  # should be 255
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
                    'type': FillSymbol,
                    'levels': [{
                        'type': SimpleFillSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0.0,
                                'B': 0.0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': LineSymbol,
                                'levels': [{
                                    'type': SimpleLineSymbolLayer,
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'width': 1.0,
                                    'line_type': 'solid',
                                    'color':
                                        {
                                            'R': 0.0,
                                            'G': 257.0,  # should be 255
                                            'B': 0,
                                            'is_null': False,
                                            'dither': True
                                        }
                                },
                                    {
                                        'type': SimpleLineSymbolLayer,
                                        'enabled': False,
                                        'locked': True,
                                        'color_model': 'rgb',
                                        'width': 2.0,
                                        'line_type': 'solid',
                                        'color':
                                            {
                                                'R': 0.0,
                                                'G': 0.0,
                                                'B': 303.0,  # should be 255
                                                'is_null': False,
                                                'dither': True
                                            }
                                    }
                                ]
                            }
                    },
                        {
                            'type': SimpleFillSymbolLayer,
                            'enabled': True,
                            'locked': True,
                            'color_model': 'rgb',
                            'color':
                                {
                                    'R': 0.0,
                                    'G': 257.0,  # should be 255
                                    'B': 0.0,
                                    'is_null': False,
                                    'dither': True
                                },
                            'outline_symbol':
                                {
                                    'type': LineSymbol,
                                    'levels': [{
                                        'type': SimpleLineSymbolLayer,
                                        'enabled': True,
                                        'locked': False,
                                        'color_model': 'rgb',
                                        'width': 2.0,
                                        'line_type': 'solid',
                                        'color':
                                            {
                                                'R': 129.0,  # should be 110
                                                'G': 129.0,  # should be 110
                                                'B': 129.0,  # should be 110
                                                'is_null': False,
                                                'dither': True
                                            }
                                    },
                                        {
                                            'type': SimpleLineSymbolLayer,
                                            'enabled': True,
                                            'locked': True,
                                            'color_model': 'rgb',
                                            'width': 1.0,
                                            'line_type': 'dashed',
                                            'color':
                                                {
                                                    'R': 289.0,  # should be 255
                                                    'G': 0.0,
                                                    'B': 0.0,
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
                    'type': FillSymbol,
                    'levels': [{
                        'type': SimpleFillSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0.0,
                                'B': 0.0,
                                'is_null': False,
                                'dither': False
                            },
                        'outline_symbol':
                            {
                                'type': LineSymbol,
                                'levels': [{
                                    'type': CartographicLineSymbolLayer,
                                    'enabled': True,
                                    'locked': False,
                                    'color_model': 'rgb',
                                    'color':
                                        {
                                            'R': 0.0,
                                            'G': 0,
                                            'B': 303,  # should be 255
                                            'is_null': False,
                                            'dither': True
                                        },
                                    'width': 4,
                                    'cap': 'round',
                                    'join': 'bevel',
                                    'offset': -7,
                                    'pattern_interval': 1.0
                                }
                                ]
                            }
                    }
                    ]
                },
            'v10_5.bin':
                {
                    'skip': True,
                    'type': FillSymbol,
                    'levels': [None]
                }
        },

    'line_bin':
        {
            '3d simple line symbol width 8.bin':
                {
                    'skip': True,
                    'type': LineSymbol,
                    'levels': [None]
                },
            '3d texture line symbol width 8.bin':
                {
                    'type': LineSymbol,
                    'skip': True,
                    'levels': [None]
                },
            'Cartographic line both arrow.bin':
                {
                    'type': LineSymbol,
                    'skip': True
                },
            'Cartographic line end arrow.bin':
                {
                    'type': LineSymbol,
                    'skip': True
                },
            'Cartographic line start arrow.bin':
                {
                    'type': LineSymbol,
                    'skip': True
                },
            'Cartographic line symbol width 8.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'butt',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line bevel join.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'butt',
                        'join': 'bevel',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line offset -4.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'butt',
                        'join': 'miter',
                        'offset': -4,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line offset 5.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'butt',
                        'join': 'miter',
                        'offset': 5,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line round join.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'butt',
                        'join': 'round',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line round.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'round',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line round width 4.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 4,
                        'cap': 'round',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }]
                },
            'Cartographic line round width 4 disabled.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': False,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 4,
                        'cap': 'round',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line square.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 1.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 0.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 00.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 01.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 10.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 11.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7 pattern 1.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Cartographic line square pattern interval 7.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': CartographicLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
                                'G': 0,
                                'B': 0,
                                'is_null': False,
                                'dither': False
                            },
                        'width': 7.9999999,
                        'cap': 'square',
                        'join': 'miter',
                        'offset': 0,
                        'pattern_interval': 7.0
                    }
                    ]
                },
            'Dash dot dot.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dash dot dot',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dash dot',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dashed',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'dotted',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'skip': True,
                    'levels': [None]
                },
            'Line disabled.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': False,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': True,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'skip': True,
                    'levels': [None]
                },
            'Null.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'null',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'skip': True,
                    'levels': [None]
                },
            'Solid 1.bin':
                {
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'width': 1.0,
                        'line_type': 'solid',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'levels': [{
                        'type': SimpleLineSymbolLayer,
                        'enabled': True,
                        'locked': False,
                        'color_model': 'rgb',
                        'color':
                            {
                                'R': 289.0,  # should be 255
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
                    'type': LineSymbol,
                    'levels': [
                        {
                            'type': SimpleLineSymbolLayer,
                            'enabled': True,
                            'locked': False,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 289.0,  # should be 255
                                    'G': 0,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': False
                                }
                        },
                        {
                            'type': SimpleLineSymbolLayer,
                            'enabled': True,
                            'locked': True,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 129.0,  # should be 110
                                    'G': 129.0,
                                    'B': 129.0,
                                    'is_null': False,
                                    'dither': True
                                }
                        }
                    ]
                },
            'Three levels.bin':
                {
                    'type': LineSymbol,
                    'levels': [
                        {
                            'type': SimpleLineSymbolLayer,
                            'enabled': True,
                            'locked': False,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'dotted',
                            'color':
                                {
                                    'R': 289.0,  # should be 255
                                    'G': 0,
                                    'B': 0,
                                    'is_null': False,
                                    'dither': False
                                }
                        },
                        {
                            'type': SimpleLineSymbolLayer,
                            'enabled': True,
                            'locked': True,
                            'color_model': 'rgb',
                            'width': 1.0,
                            'line_type': 'dash dot',
                            'color':
                                {
                                    'R': 129.0,  # should be 110
                                    'G': 129.0,
                                    'B': 129.0,
                                    'is_null': False,
                                    'dither': True
                                }
                        },
                        {
                            'type': SimpleLineSymbolLayer,
                            'enabled': False,
                            'locked': True,
                            'color_model': 'rgb',
                            'width': 2.0,
                            'line_type': 'solid',
                            'color':
                                {
                                    'R': 0.0,
                                    'G': 257.0,  # should be 255
                                    'B': 0.0,
                                    'is_null': False,
                                    'dither': True
                                }
                        }
                    ]
                }

        }
}


class TestSymbols(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def run_symbol_test(self, path):
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
                symbol = read_symbol(f)
                self.compareSymbol(symbol, expected_symbol)

    def compareSimpleOutlineLayer(self, layer, expected):
        self.assertTrue(isinstance(layer, SimpleLineSymbolLayer))
        self.assertEqual(layer.color_model, expected['color_model'])
        self.assertEqual(layer.color, expected['color'])
        self.assertEqual(layer.width, expected['width'])
        self.assertEqual(layer.line_type, expected['line_type'])

    def compareCartographicOutlineLayer(self, layer, expected):
        self.assertTrue(isinstance(layer, CartographicLineSymbolLayer))
        self.assertEqual(layer.color_model, expected['color_model'])
        self.assertEqual(layer.color, expected['color'])
        self.assertAlmostEqual(layer.width, expected['width'], 3)
        self.assertAlmostEqual(layer.offset, expected['offset'], 3)
        self.assertEqual(layer.cap, expected['cap'])
        self.assertEqual(layer.join, expected['join'])
        self.assertEqual(layer.pattern_interval, expected['pattern_interval'])

    def compareSymbol(self, symbol, expected):
        self.assertTrue(isinstance(symbol, expected['type']))
        self.assertEqual(len(symbol.levels), len(expected['levels']))
        for i in range(len(symbol.levels)):
            expected_layer = expected['levels'][i]
            layer = symbol.levels[i]
            self.assertTrue(isinstance(layer, expected_layer['type']))
            self.assertEqual(layer.enabled, expected_layer['enabled'])
            self.assertEqual(layer.locked, expected_layer['locked'])
            self.assertEqual(layer.color_model, expected_layer['color_model'])
            self.assertEqual(layer.color, expected_layer['color'])
            if isinstance(layer, SimpleLineSymbolLayer):
                self.compareSimpleOutlineLayer(layer, expected_layer)
            elif isinstance(layer, CartographicLineSymbolLayer):
                self.compareCartographicOutlineLayer(layer, expected_layer)
            elif isinstance(layer, SimpleFillSymbolLayer):
                if 'outline_layer' in expected_layer:
                    self.compareSimpleOutlineLayer(layer.outline_layer, expected_layer['outline_layer'])
                elif 'outline_symbol' in expected_layer:
                    self.compareSymbol(layer.outline_symbol, expected_layer['outline_symbol'])
                else:
                    self.assertTrue(False, 'unknown outline type')

    def testLines(self):
        path = os.path.join('styles', 'line_bin')
        self.run_symbol_test(path)

    def testFills(self):
        path = os.path.join('styles', 'fill_bin')
        self.run_symbol_test(path)


if __name__ == '__main__':
    unittest.main()
