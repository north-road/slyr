"""
SLYR algorithms
"""

from .add_layers_from_mxd import AddLayersFromMxd
from .annotation_class_to_gpkg import ConvertAnnotationClassToGeopackage
from .set_style_from_lyr import StyleFromLyr
from .mxd_to_qgs import ConvertMxdToQgs
from .lyr_to_qlr import LyrToQlr
from .lyr_to_qml import LyrToQml
from .lyr_to_style_xml import LyrToStyleXml
from .style_to_gpl import StyleToGpl
from .style_to_xml import StyleToQgisXml
from .stylx_to_xml import StylxToQgisXml
from .stylx_to_gpl import StylxToGpl
from .xml_to_stylx import XmlToStylx
from .gpl_to_stylx import GplToStylx
from .convert_mxd_and_data import ConvertMxdAndData
from .pmf_to_qgs import ConvertPmfToQgs
from .sxd_to_qgs import ConvertSxdToQgs
from .export_structure_to_json import ExportStructureToJson
from .avl_to_qml import AvlToQml
from .convert_annotations import ConvertAnnotations
from .convert_project_data import ConvertProjectData
from .extract_sde_connection_details import ExtractSDEConnectionDetails
from .hyperlinks_to_tables import ExtractHyperlinksToTables
