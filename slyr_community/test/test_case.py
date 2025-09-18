import unittest

from qgis.core import QgsSettings


class SlyrTestCase(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        settings = QgsSettings()
        settings.setValue(
            "connections/ows/items/wms/connections/items/Test WMS 1/url",
            "https://gisservices.information.qld.gov.au/arcgis/services/Imagery/QldBase_AllUsers/MapServer/WMSServer?",
        )
        settings.setValue(
            "connections/ows/items/wms/connections/items/Test WMS 1/username",
            "my username",
        )
        settings.setValue(
            "connections/ows/items/wms/connections/items/Test WMS 1/password",
            "my password",
        )

        settings.setValue(
            "connections/ows/items/wms/connections/items/Test WMST/url",
            "https://basemap.de/dienste/wmts_capabilities_web_raster.xml",
        )
        settings.setValue(
            "connections/ows/items/wms/connections/items/Test WMST/username",
            "my username2",
        )
        settings.setValue(
            "connections/ows/items/wms/connections/items/Test WMST/password",
            "my password2",
        )

        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS/url",
            "https://www.mrt.tas.gov.au/web-services/wfs",
        )
        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS/username",
            "my username2",
        )
        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS/password",
            "my password2",
        )

        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS2/url",
            "https://www.tas.gov.au/web-services/wfs",
        )
        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS2/authcfg", "myAuthId"
        )

        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS3/url",
            "https://geo.limburg.be/arcgis/services/Mobiliteit/MapServer/WFSServer",
        )
        settings.setValue(
            "connections/ows/items/wfs/connections/items/Test WFS3/authcfg", "myAuthId"
        )

        settings.setValue(
            "connections/xyz/items/Test XYZ/url",
            "http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        )
        settings.setValue("connections/xyz/items/Test XYZ/authcfg", "myAuthId")

        settings.setValue(
            "connections/xyz/items/Test XYZ2/url",
            "http://a.cartocdn.com/light_all/{z}/{x}/{y}.png",
        )
        settings.setValue("connections/xyz/items/Test XYZ2/username", "myUser")
        settings.setValue("connections/xyz/items/Test XYZ2/password", "myPassword")

        settings.setValue(
            "connections/xyz/items/Test XYZ3/url",
            "http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1",
        )
        settings.setValue("connections/xyz/items/Test XYZ3/username", "myUser")
        settings.setValue("connections/xyz/items/Test XYZ3/password", "myPassword")

        settings.setValue(
            "connections/xyz/items/Test XYZ4/url",
            "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        )
        settings.setValue("connections/xyz/items/Test XYZ4/authcfg", "myAuthId3")

        settings.setValue(
            "connections/arcgisfeatureserver/items/Test Arc/url",
            "https://services.arcgis.com/V6ZHFr6zdgNZuVG0/ArcGIS/rest/services/Aggregation_of_USA_Major_Cities_by_hexagon_bins_(3)/FeatureServer/",
        )
        settings.setValue(
            "connections/arcgisfeatureserver/items/Test Arc/username", "my username2"
        )
        settings.setValue(
            "connections/arcgisfeatureserver/items/Test Arc/password", "my password2"
        )

        settings.setValue(
            "connections/arcgisfeatureserver/items/Test Arc3/url",
            "https://services.arcgis.com/XTtANUDT8Va4DLwI/ArcGIS/rest/services/NZ_School_Zone_boundaries/FeatureServer/",
        )
        settings.setValue(
            "connections/arcgisfeatureserver/items/Test Arc3/authcfg", "myAuthId"
        )

        settings.setValue(
            "connections/arcgisfeatureserver/items/Test MS1/url",
            "https://environment.data.gov.uk/arcgis/rest/services/RPA/CropMapOfEngland2020/MapServer",
        )
        settings.setValue(
            "connections/arcgisfeatureserver/items/Test MS1/authcfg", "myAuthId"
        )

        settings.setValue(
            "connections/arcgisfeatureserver/items/Test MS2/url",
            "https://cityplanmaps.goldcoast.qld.gov.au/arcgis/rest/services/CityPlan/Overlays/MapServer",
        )
        settings.setValue(
            "connections/arcgisfeatureserver/items/Test MS2/username", "my_user"
        )
        settings.setValue(
            "connections/arcgisfeatureserver/items/Test MS2/password", "my_pass"
        )

        settings.setValue("PostgreSQL/connections/my db/host", "my_db_host")
        settings.setValue("PostgreSQL/connections/my db/database", "my_db")
        settings.setValue("PostgreSQL/connections/my db/username", "my_user")
        settings.setValue("PostgreSQL/connections/my db/password", "my_pass")

        settings.setValue("PostgreSQL/connections/my db2/host", "my_db_host2")
        settings.setValue("PostgreSQL/connections/my db2/database", "my_db2")
        settings.setValue("PostgreSQL/connections/my db2/authcfg", "my_auth")

        settings.setValue("Oracle/connections/my db/host", "my_oracle_db_host")
        settings.setValue("Oracle/connections/my db/database", "my_db")
        settings.setValue("Oracle/connections/my db/username", "my_user")
        settings.setValue("Oracle/connections/my db/password", "my_pass")

        settings.setValue("Oracle/connections/my db2/host", "my_oracle_db_host2")
        settings.setValue("Oracle/connections/my db2/database", "my_db2")
        settings.setValue("Oracle/connections/my db2/authcfg", "my_auth")

        settings.setValue("MSSQL/connections/my db/host", "my_mssql_db_host")
        settings.setValue("MSSQL/connections/my db/database", "my_db")
        settings.setValue("MSSQL/connections/my db/username", "my_user")
        settings.setValue("MSSQL/connections/my db/password", "my_pass")

        settings.setValue("MSSQL/connections/my db2/host", "my_mssql_db_host2")
        settings.setValue("MSSQL/connections/my db2/database", "my_db2")
        settings.setValue("MSSQL/connections/my db2/authcfg", "my_auth")

    @classmethod
    def tearDownClass(cls):
        settings = QgsSettings()
        settings.remove("connections/ows/items/wms/connections/items/Test WMS 1")
        settings.remove("connections/ows/items/wms/connections/items/Test WMST")
        settings.remove("connections/ows/items/wfs/connections/items/Test WFS")
        settings.remove("connections/ows/items/wfs/connections/items/Test WFS2")
        settings.remove("connections/ows/items/wfs/connections/items/Test WFS3")
        settings.remove("connections/xyz/items/Test XYZ")
        settings.remove("connections/xyz/items/Test XYZ2")
        settings.remove("connections/xyz/items/Test XYZ3")
        settings.remove("connections/xyz/items/Test XYZ4")
        settings.remove("connections/arcgisfeatureserver/items/Test Arc")
        settings.remove("connections/arcgisfeatureserver/items/Test Arc2")
        settings.remove("connections/arcgisfeatureserver/items/Test Arc3")
        settings.remove("connections/arcgisfeatureserver/items/Test MS1")
        settings.remove("connections/arcgisfeatureserver/items/Test MS2")
        settings.remove("PostgreSQL/connections/my db")
        settings.remove("PostgreSQL/connections/my db2")
        settings.remove("Oracle/connections/my db")
        settings.remove("Oracle/connections/my db2")
        settings.remove("MSSQL/connections/my db")
        settings.remove("MSSQL/connections/my db2")
