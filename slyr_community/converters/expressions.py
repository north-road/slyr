#!/usr/bin/env python

# /***************************************************************************
# expressions.py
# ----------
# Date                 : September 2019
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
Expression conversion
"""

import re

from qgis.core import QgsExpression

from .context import Context
from ..parser.objects.annotation_jscript_engine import AnnotationJScriptEngine
from ..parser.objects.annotation_python_engine import AnnotationPythonEngine
from ..parser.objects.annotation_vbscript_engine import AnnotationVBScriptEngine


class ExpressionConverter:
    """
    Converts expressions to QGIS format
    """

    FUNCTION_MAP = {
        'ucase': 'upper',
        'lcase': 'lower',
        'replace': 'replace',
        'chr': 'char'
    }

    @staticmethod
    def convert(expression: str, engine, advanced, context: Context):  # pylint: disable=too-many-branches
        """
        Converts an expression which uses the specified engine
        """
        expression_type = ''
        if isinstance(engine, AnnotationVBScriptEngine):
            expression_type = 'VBScript'
        elif isinstance(engine, AnnotationPythonEngine):
            expression_type = 'Python'
        elif isinstance(engine, AnnotationJScriptEngine):
            expression_type = 'JScript'

        if advanced:
            if context.unsupported_object_callback:
                if context.layer_name:
                    context.unsupported_object_callback(
                        '{}: Cannot automatically convert advanced {} expression: {}'.format(context.layer_name,
                                                                                             expression_type,
                                                                                             expression),
                        level=Context.WARNING)
                elif context.symbol_name:
                    context.unsupported_object_callback(
                        '{}: Cannot automatically convert advanced {} expression: {}'.format(context.symbol_name,
                                                                                             expression_type,
                                                                                             expression),
                        level=Context.WARNING)
                else:
                    context.unsupported_object_callback(
                        'Cannot automatically convert advanced {} expression: {}'.format(expression_type, expression),
                        level=Context.WARNING)
            return expression

        if isinstance(engine, AnnotationVBScriptEngine):
            res = ExpressionConverter.convert_vbscript_expression(expression, context)
        elif isinstance(engine, AnnotationPythonEngine):
            res = ExpressionConverter.convert_python_expression(expression)
        elif isinstance(engine, AnnotationJScriptEngine):
            res = ExpressionConverter.convert_js_expression(expression)
        else:
            res = ExpressionConverter.convert_esri_expression(expression)

        exp = QgsExpression(res)
        if not advanced and exp.hasParserError() and context.unsupported_object_callback:
            if context.layer_name:
                context.unsupported_object_callback(
                    '{}: Could not automatically convert {} expression:\n{}\nPlease check and repair this expression'.format(
                        context.layer_name,
                        expression_type,
                        expression),
                    level=Context.WARNING)
            elif context.symbol_name:
                context.unsupported_object_callback(
                    '{}: Cannot automatically convert {} expression:\n{}\nPlease check and repair this expression'.format(
                        context.symbol_name,
                        expression_type, expression),
                    level=Context.WARNING)
            else:
                context.unsupported_object_callback(
                    'Cannot automatically convert {} expression:\n{}\nPlease check and repair this expression'.format(
                        expression_type, expression),
                    level=Context.WARNING)

        return res

    @staticmethod
    def convert_esri_expression(expression: str):
        """
        Rudimentary ESRI to QGIS expression conversion
        """
        # super dangerous!
        expression = expression.replace('"', "'")
        expression = expression.replace('chr(13)', "'\\n'")

        # super dangerous, also should probably be concat to handle nulls
        expression = expression.replace('&', ' || ')

        expression = re.sub("\\[([\\w.\\- _$#:]+)]", '"\\1"', expression, flags=re.UNICODE)

        return expression

    @staticmethod
    def convert_vbscript_expression(expression: str, context: Context):
        """
        Rudimentary ESRI to QGIS expression conversion
        """
        # super dangerous!
        expression = expression.replace('"', "'")
        expression = expression.replace('chr(13)', "'\\n'")

        expression = re.sub('vbnewline', "'\\n'", expression, flags=re.IGNORECASE)

        # super dangerous, also should probably be concat to handle nulls
        expression = expression.replace('&', ' || ')

        if context.dataset_name:
            expression = re.sub("\\[{}\\.([\\w.\\- _$#:/]+)]".format(
                context.dataset_name.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')), '"\\1"',
                                expression, flags=re.UNICODE)
        expression = re.sub("\\[([\\w.\\- _$#:/]+)]", '"\\1"', expression, flags=re.UNICODE)
        for esri, qgis in ExpressionConverter.FUNCTION_MAP.items():
            expression = re.sub(r"{}\s*\(".format(esri), '{}('.format(qgis), expression, flags=re.IGNORECASE)

        return expression

    @staticmethod
    def convert_python_expression(expression: str):
        """
        Rudimentary Python to QGIS expression conversion
        """
        # super dangerous!
        expression = re.sub("\\[([\\w.\\- _$#:]+)]", '"\\1"', expression, flags=re.UNICODE)
        return expression

    @staticmethod
    def convert_js_expression(expression: str):
        """
        Rudimentary JS to QGIS expression conversion
        """
        # super dangerous!
        expression = re.sub("\\[([\\w.\\- _$#:]+)]", '"\\1"', expression, flags=re.UNICODE)
        return expression

    @staticmethod
    def convert_esri_sql(expression: str):
        """
        Rudimentary ESRI SQL to QGIS expression conversion
        """
        expression = re.sub("\\[([\\w.\\- _$#:]+)]", '"\\1"', expression, flags=re.UNICODE)
        expression = re.sub(r"#(\d+-\d+-\d+\s+\d+:\d+:\d+)#", "'\\1'", expression, flags=re.UNICODE)
        return expression
