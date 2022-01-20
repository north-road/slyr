"""
QGIS UI integrations
"""

from .style_items import StyleDropHandler
from .browser import SlyrDataItemProvider
from .lyr_items import LyrDropHandler
from .mxd_items import (
    MxdDropHandler,
    MxdProjectOpenHandler
)
from .dat_items import DatDropHandler
from .name_drop_handler import NameDropHandler
from .layout_drop_handler import LayoutDropHandler
