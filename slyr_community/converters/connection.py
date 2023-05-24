#!/usr/bin/env python

# /***************************************************************************
# color_ramp.py
# ----------
# Date                 : October 2019
# copyright            : (C) 2019 by Nyall Dawson
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Connection conversion utilities
"""

import re
from pathlib import Path
from typing import Tuple, Optional

from qgis.core import QgsDataSourceUri

from .context import Context
from ..parser.exceptions import (UnreadableSymbolException,
                                 NotImplementedException,
                                 UnknownClsidException,
                                 EmptyDocumentException,
                                 DocumentTypeException)
from ..parser.objects.property_set import PropertySet
from ..parser.streams.sde_connection import SDEConnection


class ConnectionConverter:
    """
    Connection converter
    """

    @staticmethod
    def convert_sde_connection(connection: Path,  # pylint: disable=too-many-return-statements,too-many-branches
                               context: Context) -> Optional[Tuple[QgsDataSourceUri, str]]:
        """
        Tries to convert an SDE connection at the specified path to a QgsDataSourceUri equivalent
        """
        context.file_name = str(connection)
        if not connection.exists():
            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    f'Could not convert SDE connection file: "{context.file_name}". This file does not exist',
                    level=Context.WARNING)
            return None

        with open(connection, 'rb') as f:
            try:
                doc = SDEConnection(f)
            except UnknownClsidException:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
                return None
            except UnreadableSymbolException:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
                return None
            except NotImplementedException:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
                return None
            except UnicodeDecodeError:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" - unknown connection format. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
                return None
            except EmptyDocumentException:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" - connection file is corrupt.',
                        level=Context.WARNING)
                return None
            except DocumentTypeException:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" - connection file is corrupt.',
                        level=Context.WARNING)
                return None

            return ConnectionConverter.convert_connection(doc.connection, context)

    @staticmethod
    def convert_connection(connection: PropertySet,  # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
                           context: Context) -> Optional[Tuple[QgsDataSourceUri, str]]:
        """
        Tries to convert extract connection properties to a QgsDataSourceUri equivalent
        """
        db_client = connection.properties.get('DBCLIENT')

        if not db_client and 'INSTANCE' in connection.properties:
            # try to guess client from instance
            instance = connection.properties['INSTANCE']

            oracle_instance = re.search(r'^sde:oracle(?:11g)$', instance, re.IGNORECASE)
            if oracle_instance:
                db_client = 'oracle'

            if not db_client:
                sql_server_instance = re.search(r'^sde:sqlserver:.*$', instance, re.IGNORECASE)
                if sql_server_instance:
                    db_client = 'sqlserver'

        if not db_client:
            if context.unsupported_object_callback:
                if context.file_name:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}". Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
                else:
                    context.unsupported_object_callback(
                        'Could not convert SDE connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)

            return None

        if db_client == 'oracle':
            if 'INSTANCE' not in connection.properties:
                if context.unsupported_object_callback:
                    if context.file_name:
                        context.unsupported_object_callback(
                            f'Could not convert SDE connection file: "{context.file_name}" to an Oracle connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING)
                    else:
                        context.unsupported_object_callback(
                            'Could not convert SDE connection to an Oracle connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING)
                return None

            instance = connection.properties['INSTANCE']

            db_search = re.search(r'^sde:oracle(?:11g)?[$:](.*?)(?:[/:](.*?))?$', instance, re.IGNORECASE)
            if db_search:
                _ = db_search.group(1)  # server
                db_name = db_search.group(2) or ''

                uri = QgsDataSourceUri()
                uri.setConnection('', '1521', db_name, '', '')
                uri.setUseEstimatedMetadata(True)

                return uri, 'oracle'
            elif connection.properties.get('SERVER'):
                server = connection.properties['SERVER']
                db_name = connection.properties.get('DATABASE')

                uri = QgsDataSourceUri()
                uri.setConnection(server, '1521', db_name, '', '')

                uri.setUseEstimatedMetadata(True)

                return uri, 'oracle'
            else:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" to an Oracle connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
            return None
        elif db_client == 'postgresql':
            if 'INSTANCE' not in connection.properties:
                if context.unsupported_object_callback:
                    if context.file_name:
                        context.unsupported_object_callback(
                            f'Could not convert SDE connection file: "{context.file_name}" to an PostgreSQL connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING)
                    else:
                        context.unsupported_object_callback(
                            'Could not convert SDE connection to an PostgreSQL connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING)
                return None

            instance = connection.properties['INSTANCE']

            db_search = re.search(r'^sde:postgresql[$:](.*?)[,](.*?)$', instance, re.IGNORECASE)
            if db_search:
                server = db_search.group(1)
                port = db_search.group(2)

                uri = QgsDataSourceUri()
                uri.setConnection(server, port, connection.properties.get('DATABASE', ''),
                                  connection.properties.get('USER', ''), '')
                uri.setUseEstimatedMetadata(True)

                return uri, 'postgres'

            else:
                if context.unsupported_object_callback:
                    context.unsupported_object_callback(
                        f'Could not convert SDE connection file: "{context.file_name}" to an PostgreSQL connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.WARNING)
            return None
        elif db_client == 'sqlserver':
            if 'SERVER' not in connection.properties:
                if context.unsupported_object_callback:
                    if context.file_name:
                        context.unsupported_object_callback(
                            f'Could not convert SDE connection file: "{context.file_name}" to an SQL Server connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING)
                    else:
                        context.unsupported_object_callback(
                            'Could not convert SDE connection to an SQL Server connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                            level=Context.WARNING)
                return None

            server = connection.properties['SERVER']

            if 'INSTANCE' in connection.properties:
                db_search = re.search(r'^sde:sqlserver[$:].*?,(\d+)$', connection.properties['INSTANCE'], re.IGNORECASE)
                if db_search:
                    server += ',' + db_search.group(1)  # add port number as a ",PORT" suffix. Apparently this is the only way to get a non-standard SQL server port for QGIS!

            uri = QgsDataSourceUri()
            uri.setConnection(server, '', connection.properties['DATABASE'], '', '')
            return uri, 'mssql'

        if context.unsupported_object_callback:
            if context.file_name:
                context.unsupported_object_callback(
                    f'Unsupported database type "{connection.properties["DBCLIENT"]}" in SDE connection file: "{context.file_name}". Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING)
            else:
                context.unsupported_object_callback(
                    f'Unsupported database type "{connection.properties["DBCLIENT"]}" in SDE connection. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                    level=Context.WARNING)
        return None
