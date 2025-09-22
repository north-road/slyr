"""
Converts .qml to ArcGIS Pro .stylx databases
"""

import re
from typing import Tuple
from pathlib import Path

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsMemoryProviderUtils,
    QgsFields,
    QgsWkbTypes,
    QgsStyleEntityVisitorInterface,
    QgsStyle,
    QgsProcessingException,
)
from qgis.PyQt.QtXml import QDomDocument

from .algorithm import SlyrAlgorithm
from .utils import AlgorithmUtils


class QmlStyleEntityVisitor(QgsStyleEntityVisitorInterface):
    def __init__(self, style: QgsStyle, feedback):
        super().__init__()
        self._parent_names = []
        self._style = style
        self._feedback = feedback

    def visit(self, entity):
        name = (" ".join(self._parent_names) + " " + entity.description).strip()

        if not name:
            name = {
                QgsStyle.StyleEntity.SymbolEntity: "Symbol",
                QgsStyle.StyleEntity.ColorrampEntity: "Color Ramp",
                QgsStyle.StyleEntity.TextFormatEntity: "Text Format",
                QgsStyle.StyleEntity.LabelSettingsEntity: "Label Settings",
            }.get(entity.entity.type(), "Object")

        candidate = name
        i = 1
        exists = True
        while exists:
            exists = candidate in self._style.allNames(entity.entity.type())
            if not exists:
                break

            i += 1
            candidate = name + " ({})".format(i)

        self._feedback.pushInfo("Found {}".format(candidate))
        self._style.addEntity(candidate, entity.entity, True)
        return True

    def visitEnter(self, node):
        if node.type in (
            QgsStyleEntityVisitorInterface.NodeType.Layer,
            QgsStyleEntityVisitorInterface.NodeType.SymbolRule,
            QgsStyleEntityVisitorInterface.NodeType.Annotation,
        ):
            self._parent_names.append(node.description)

        return True

    def visitExit(self, node):
        if node.type in (
            QgsStyleEntityVisitorInterface.NodeType.Layer,
            QgsStyleEntityVisitorInterface.NodeType.SymbolRule,
            QgsStyleEntityVisitorInterface.NodeType.Annotation,
        ):
            self._parent_names = self._parent_names[:-1]

        return True


class QmlToStylex(SlyrAlgorithm):
    """
    Converts .qml to ArcGIS Pro .stylx databases
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return QmlToStylex()

    def name(self):
        return "qmltostylx"

    def displayName(self):
        return "Convert QML to STYLX"

    def shortDescription(self):
        return "Convert a QGIS QML style file to an ArcGIS Pro STYLX database"

    def group(self):
        return "ArcGIS Pro"

    def groupId(self):
        return "arcgispro"

    def shortHelpString(self):
        return (
            "Converts a QGIS QML style definition to an "
            "ArcGIS Pro STYLX database containing all symbols from the QML "
            "style."
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT, "Input QML file", fileFilter="QML files (*.qml *.QML)"
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                "Destination stylx database",
                fileFilter="STYLX files (*.stylx)",
            )
        )

    def autogenerateParameterValues(self, rowParameters, changedParameter, mode):
        if changedParameter == self.INPUT:
            input_file = rowParameters.get(self.INPUT)
            if input_file:
                input_path = Path(input_file)
                if input_path.exists():
                    return {self.OUTPUT: input_path.with_suffix(".stylx").as_posix()}

        return {}

    @staticmethod
    def is_raster_qml(path: str) -> bool:
        """
        Returns True if a QML file is a raster style
        """
        doc = QDomDocument()
        with open(path, "r", encoding="utf-8") as f:
            doc.setContent(f.read())

        root = doc.firstChildElement("qgis")
        if root.isNull():
            return False

        return not root.firstChildElement("pipe").isNull()

    @staticmethod
    def qml_geometry_type(path: str) -> Tuple[bool, QgsWkbTypes.Type, str]:
        """
        Returns the geometry type for a QML file
        """
        doc = QDomDocument()
        with open(path, "r", encoding="utf-8") as f:
            raw_content = f.read()
        doc.setContent(raw_content)

        root = doc.firstChildElement("qgis")
        if root.isNull():
            return (
                False,
                QgsWkbTypes.Type.Unknown,
                "Root <qgis> element could not be found",
            )

        if not root.firstChildElement("layerGeometryType").isNull():
            try:
                qml_geometry_type = int(
                    root.firstChildElement("layerGeometryType").text()
                )
                return (
                    True,
                    {
                        0: QgsWkbTypes.Type.Point,
                        1: QgsWkbTypes.Type.LineString,
                        2: QgsWkbTypes.Type.Polygon,
                        4: QgsWkbTypes.Type.NoGeometry,
                    }.get(qml_geometry_type, QgsWkbTypes.Type.Unknown),
                    "",
                )
            except ValueError:
                pass

        # fallback -- try looking for first symbol type. Works for very old QML files
        match = re.match(r'^.*?type="(marker|fill|line)".*$', raw_content, re.DOTALL)
        if match:
            return (
                True,
                {
                    "marker": QgsWkbTypes.Type.Point,
                    "line": QgsWkbTypes.Type.LineString,
                    "fill": QgsWkbTypes.Type.Polygon,
                }.get(match.group(1), QgsWkbTypes.Type.Unknown),
                "",
            )

        return (
            False,
            QgsWkbTypes.Type.Unknown,
            'Could not read "layerGeometryType" from QML',
        )

    def processAlgorithm(
        self,
        # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        parameters,
        context,
        feedback,
    ):
        raise QgsProcessingException(
            "This algorithm is available in the licensed version of SLYR only - please see https://north-road.com/slyr/ for details"
        )

    # pylint: enable=missing-docstring,unused-argument
