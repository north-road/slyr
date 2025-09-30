"""
Connection conversion utilities
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import re
from pathlib import Path
from typing import Tuple, Optional, Dict, List

from qgis.core import QgsDataSourceUri

from .context import Context
from ..parser.exceptions import (
    UnreadableSymbolException,
    NotImplementedException,
    UnknownClsidException,
    EmptyDocumentException,
    DocumentTypeException,
)
from ..parser.objects.property_set import PropertySet
from ..parser.streams.sde_connection import SDEConnection


class FdlConnectionParser:
    """
    Parses FDL connection strings
    """

    @staticmethod
    def parse_fdl(fdl_contents: str) -> Dict:
        """
        Parses Fdl connection properties to a dictionary
        """
        tokens = FdlConnectionParser.extract_tokens(fdl_contents)
        if not tokens:
            return {}

        properties = FdlConnectionParser.tokens_to_dict(tokens[1:])
        properties["version"] = tokens[0]
        return properties

    @staticmethod
    def tokens_to_dict(tokens: List) -> Dict:
        """
        Converts tokens from a FDL file to a readable dictionary
        """
        res = {}
        current_key = ""
        for token in tokens:
            if not current_key:
                current_key = token
            else:
                if current_key in ("COORDSYS",):
                    if token:
                        value_tokens = token.split("|")
                        if value_tokens:
                            res[current_key] = {
                                "name": value_tokens[1],
                                "wkt": value_tokens[2].replace('""', '"'),
                            }
                        else:
                            res[current_key] = None
                    else:
                        res[current_key] = None
                else:
                    value_tokens = FdlConnectionParser.extract_tokens(token)
                    if not value_tokens:
                        res[current_key] = None
                    elif len(value_tokens) == 1:
                        res[current_key] = FdlConnectionParser.process_literal(
                            value_tokens[0]
                        )
                    else:
                        res[current_key] = FdlConnectionParser.tokens_to_dict(
                            value_tokens
                        )
                current_key = ""

        return res

    @staticmethod
    def process_literal(token):
        """
        Processes a token and returns as a Python object
        """
        if isinstance(token, str):
            if token.lower() == "no":
                return False
            if token.lower() == "yes":
                return True

            try:
                int_value = int(token)
                float_value = float(token)
                if int_value != float_value:
                    return float_value
                return int_value
            except ValueError:
                try:
                    return float(token)
                except ValueError:
                    pass

        return token

    @staticmethod
    def extract_tokens(string: str, delim=",") -> List[str]:
        """
        Extracts tokens from an escaped string
        """
        tokens = []
        current_token = ""
        current_escape_token = ""

        current_index = 0
        while current_index < len(string):
            char = string[current_index]
            current_index += 1
            if char not in (delim, '"'):
                current_token += char
            elif char == '"':
                this_escape_token = char
                while current_index < len(string) and string[current_index] == '"':
                    this_escape_token += '"'
                    current_index += 1

                if not current_escape_token:
                    current_escape_token = this_escape_token
                elif this_escape_token != current_escape_token:
                    current_token += this_escape_token
                else:
                    current_escape_token = ""
            else:
                if current_escape_token:
                    current_token += char
                else:
                    tokens.append(current_token)
                    current_token = ""

        if current_token:
            tokens.append(current_token)

        return tokens


class ConnectionConverter:
    """
    Connection converter
    """

    @staticmethod
    def convert_sde_connection(
        connection: Path,  # pylint: disable=too-many-return-statements,too-many-branches
        context: Context,
    ) -> Optional[Tuple[QgsDataSourceUri, str]]:
        """
        Tries to convert an SDE connection at the specified path to a QgsDataSourceUri equivalent
        """
        context.file_name = str(connection)
        if not connection.exists():
            context.push_warning(
                f'Could not convert SDE connection file: "{context.file_name}". This file does not exist',
                level=Context.WARNING,
            )
            return None

        with open(connection, "rb") as f:
            try:
                doc = SDEConnection(f)
            except UnknownClsidException:
                context.push_warning(
                    f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING,
                )
                return None
            except UnreadableSymbolException:
                context.push_warning(
                    f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING,
                )
                return None
            except NotImplementedException:
                context.push_warning(
                    f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING,
                )
                return None
            except UnicodeDecodeError:
                context.push_warning(
                    f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING,
                )
                return None
            except EmptyDocumentException:
                context.push_warning(
                    f'Could not convert SDE connection file: "{context.file_name}" - connection file is corrupt.',
                    level=Context.WARNING,
                )
                return None
            except DocumentTypeException:
                context.push_warning(
                    f'Could not convert SDE connection file: "{context.file_name}" - connection file is corrupt.',
                    level=Context.WARNING,
                )
                return None

            return ConnectionConverter.convert_connection(doc.connection, context)

    @staticmethod
    def convert_connection_string(
        connection_string: str, context: Context
    ) -> Optional[Tuple[QgsDataSourceUri, str]]:
        """
        Tries to convert an encoded SDE connection string to a
        QgsDataSourceUri equivalent
        """
        parts = connection_string.split(";")
        property_set = PropertySet()
        for part in parts:
            parsed_part = re.match(r"^(.*?)=(.*)$", part)
            if parsed_part:
                property_set.properties[parsed_part.group(1)] = parsed_part.group(2)
            else:
                return None
        return ConnectionConverter.convert_connection(property_set, context)

    @staticmethod
    def convert_connection(
        connection: PropertySet,  # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
        context: Context,
    ) -> Optional[Tuple[QgsDataSourceUri, str]]:
        """
        Tries to convert extract connection properties to a QgsDataSourceUri equivalent
        """

        db_client = connection.properties.get("DBCLIENT")

        if not db_client and "INSTANCE" in connection.properties:
            # try to guess client from instance
            instance = connection.properties["INSTANCE"]

            oracle_instance = re.search(
                r"^sde:oracle(?:10g|11g)?$", instance, re.IGNORECASE
            )
            if oracle_instance:
                db_client = "oracle"

            if not db_client:
                sql_server_instance = re.search(
                    r"^sde:sqlserver:.*$", instance, re.IGNORECASE
                )
                if sql_server_instance:
                    db_client = "sqlserver"

        if not db_client:
            if context.unsupported_object_callback:
                if context.file_name:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}". Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING,
                    )
                else:
                    properties = [p for p in connection.properties if p != "DATABASE"]
                    if properties:
                        context.unsupported_object_callback(
                            "Could not convert SDE connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                            level=Context.WARNING,
                        )
                    else:
                        context.push_warning(
                            "Connection details are incomplete, the layer source will need to be manually repaired"
                        )

            return None

        if db_client == "oracle":
            if "INSTANCE" not in connection.properties:
                if context.unsupported_object_callback:
                    if context.file_name:
                        context.unsupported_object_callback(
                            f'Could not convert SDE connection file: "{context.file_name}" to an Oracle connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING,
                        )
                    else:
                        context.unsupported_object_callback(
                            "SDE Oracle connection properties are incomplete. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                            level=Context.WARNING,
                        )
                return None

            instance = connection.properties["INSTANCE"]

            db_search = re.search(
                r"^sde:oracle(?:10g|11g)?(?:\$sde:oracle(?:10g|11g)?)?[$:](.*?)(?:[/:](.*?))?$",
                instance,
                re.IGNORECASE,
            )
            if db_search:
                server = db_search.group(1)
                db_name = db_search.group(2) or ""

                uri = QgsDataSourceUri()
                uri.setConnection(
                    server, "1521", db_name, connection.properties.get("USER") or "", ""
                )
                uri.setUseEstimatedMetadata(True)

                if context.ignore_online_sources:
                    uri.setConnection("", "", "", "")

                return uri, "oracle"
            elif connection.properties.get("SERVER"):
                server = connection.properties["SERVER"]
                db_name = connection.properties.get("DATABASE")

                uri = QgsDataSourceUri()
                uri.setConnection(
                    server, "1521", db_name, connection.properties.get("USER") or "", ""
                )

                uri.setUseEstimatedMetadata(True)

                if context.ignore_online_sources:
                    uri.setConnection("", "", "", "")

                return uri, "oracle"
            else:
                if context.file_name:
                    context.push_warning(
                        f'Could not convert SDE connection file: "{context.file_name}" to an Oracle connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING,
                    )
                else:
                    context.push_warning(
                        "SDE Oracle connection properties are incomplete. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                        level=Context.WARNING,
                    )

            return None
        elif db_client == "postgresql":
            if "INSTANCE" not in connection.properties:
                if context.unsupported_object_callback:
                    if context.file_name:
                        context.unsupported_object_callback(
                            f'Could not convert SDE connection file: "{context.file_name}" to a PostgreSQL connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING,
                        )
                    else:
                        context.unsupported_object_callback(
                            "SDE PostgreSQL connection properties are incomplete. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                            level=Context.WARNING,
                        )
                return None

            instance = connection.properties["INSTANCE"]

            db_search = re.search(
                r"^sde:postgresql[$:](.*?)(?:[,](.*?))?$", instance, re.IGNORECASE
            )
            if db_search:
                server = db_search.group(1)
                port = db_search.group(2)
                if not port:
                    port = "5432"

                uri = QgsDataSourceUri()
                uri.setConnection(
                    server,
                    port,
                    connection.properties.get("DATABASE", ""),
                    connection.properties.get("USER", ""),
                    "",
                )
                uri.setUseEstimatedMetadata(True)

                if context.ignore_online_sources:
                    uri.setConnection("", "", "", "")

                return uri, "postgres"

            else:
                if context.file_name:
                    context.push_warning(
                        f'Could not convert SDE connection file: "{context.file_name}" to an PostgreSQL connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING,
                    )
                else:
                    context.push_warning(
                        "SDE PostgreSQL connection properties are incomplete. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                        level=Context.WARNING,
                    )
            return None
        elif db_client == "sqlserver":
            server = None
            if "INSTANCE" in connection.properties:
                db_search = re.search(
                    r"^sde:sqlserver[$:](.*?)(?:,(\d+))?$",
                    connection.properties["INSTANCE"],
                    re.IGNORECASE,
                )
                if db_search:
                    server = db_search.group(1)
                    if db_search.group(2):
                        server += (
                            "," + db_search.group(2)
                        )  # add port number as a ",PORT" suffix. Apparently this is the only way to get a non-standard SQL server port for QGIS!
            elif "SERVER" in connection.properties:
                server = connection.properties["SERVER"]
                if "INSTANCE" in connection.properties:
                    db_search = re.search(
                        r"^sde:sqlserver[$:].*?,(\d+)$",
                        connection.properties["INSTANCE"],
                        re.IGNORECASE,
                    )
                    if db_search:
                        server += (
                            "," + db_search.group(1)
                        )  # add port number as a ",PORT" suffix. Apparently this is the only way to get a non-standard SQL server port for QGIS!

            if not server:
                if context.unsupported_object_callback:
                    if context.file_name:
                        context.unsupported_object_callback(
                            f'Could not convert SDE connection file: "{context.file_name}" to an SQL Server connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING,
                        )
                    else:
                        context.unsupported_object_callback(
                            "SDE SQL Server connection properties are incomplete. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                            level=Context.WARNING,
                        )
                return None

            uri = QgsDataSourceUri()
            uri.setConnection(
                server,
                "",
                connection.properties["DATABASE"],
                connection.properties.get("USER"),
                "",
            )

            if context.ignore_online_sources:
                uri.setConnection("", "", "", "")

            return uri, "mssql"

        if context.unsupported_object_callback:
            if context.file_name:
                context.unsupported_object_callback(
                    f'Unsupported database type "{connection.properties["DBCLIENT"]}" in SDE connection file: "{context.file_name}". Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING,
                )
            else:
                context.unsupported_object_callback(
                    f'Unsupported database type "{connection.properties["DBCLIENT"]}" in SDE connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING,
                )
        return None
