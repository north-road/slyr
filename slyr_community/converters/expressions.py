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
from typing import Optional

from qgis.core import QgsExpression

from .context import Context
from ..parser.objects.annotation_jscript_engine import AnnotationJScriptEngine
from ..parser.objects.annotation_python_engine import AnnotationPythonEngine
from ..parser.objects.annotation_vbscript_engine import AnnotationVBScriptEngine

# pylint: disable=simplifiable-condition


class ExpressionConverter:
    """
    Converts expressions to QGIS format
    """

    FUNCTION_MAP = {
        'ucase': 'upper',
        'lcase': 'lower',
        'replace': 'replace',
        'chr': 'char',
        'left': 'left',
        'instr': 'strpos',
        'mid' :'substr',
        'len': 'length',
        'int': 'to_int',
        'formatnumber': 'format_number'
    }

    PYTHON_OPERATOR_MAP = {
        'title': 'title',
        'lower': 'lower',
        'upper': 'upper'
    }

    PYTHON_FUNCTION_MAP = {
        'len': 'length'
    }

    @staticmethod
    def convert(expression: str, engine, advanced, context: Context) -> str:  # pylint: disable=too-many-branches
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

        if advanced and not isinstance(engine, AnnotationPythonEngine):
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

        if isinstance(engine, AnnotationVBScriptEngine) or False:
            res = ExpressionConverter.convert_vbscript_expression(expression, context)
        elif isinstance(engine, AnnotationPythonEngine) or False:
            res = ExpressionConverter.convert_python_expression(expression, context, is_advanced=advanced)
        elif isinstance(engine, AnnotationJScriptEngine) or False:
            res = ExpressionConverter.convert_js_expression(expression)
        else:
            res = ExpressionConverter.convert_esri_expression(expression, context)

        if res == '':
            return ''

        exp = QgsExpression(res)
        if (not advanced or (advanced and isinstance(engine, AnnotationPythonEngine) ) ) and exp.hasParserError() and context.unsupported_object_callback:
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
    def convert_esri_expression(expression: str, context: Context) -> str:
        """
        Rudimentary ESRI to QGIS expression conversion
        """
        if expression.strip() == '[]':
            # seen in some files!
            return ''

        # super dangerous!
        expression = expression.replace('\r\n', '\n')
        expression = expression.replace('\n\r', '\n')
        expression = expression.replace('\r', '\n')

        expression = expression.replace('"', "'")
        expression = re.sub(r"chr\(13\)", "'\\n'", expression, flags=re.IGNORECASE)

        # super dangerous, also should probably be concat to handle nulls
        expression = expression.replace('&', ' || ')

        if context.dataset_name:
            expression = re.sub("\\[{}\\.([\\w.\\- _$#:/]+)]".format(
                context.dataset_name.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)').replace('[', '\\[')), '"\\1"',
                                expression, flags=re.UNICODE)

        expression = re.sub("\\[([\\w.\\- _$#:§€Ç]+)\n*]", '"\\1"', expression, flags=re.UNICODE)

        return expression

    @staticmethod
    def convert_vbscript_expression(expression: str, context: Context) -> str:
        """
        Rudimentary ESRI to QGIS expression conversion
        """
        if expression.strip() == '[]':
            # seen in some files!
            return ''

        expression = expression.replace('\r\n', '\n')
        expression = expression.replace('\n\r', '\n')
        expression = expression.replace('\r', '\n')

        # super dangerous!
        if re.search(r"([^\"]*)'([^']+?)'([^\"]*)'([^']+?)'([^\"]*)", expression, flags=re.UNICODE):
            expression = re.sub(r'''"([^"]*)'([^']+?)'([^"]*)'([^']+?)'([^"]*)"''', r'''"\1\\'\2\\'\3\\'\4\\'\5"''', expression, flags=re.UNICODE)
        else:
            expression = re.sub(r'''"([^"]*)(?<!\\)'([^']+)(?<!\\)'([^"]*)"''', r'''"\1\\'\2\\'\3"''', expression, flags=re.UNICODE)
        while re.search(r'''"([^"]*)(?<!\\)'([^"']*)"''', expression, flags=re.UNICODE):
            expression = re.sub(r'''"([^"]*)(?<!\\)'([^"']*)"''', r'''"\1\\'\2"''', expression,
                            flags=re.UNICODE)

        expression = expression.replace('"', "'")
        expression = expression.replace('chr(13)', "'\\n'")

        expression = re.sub('vbnewline', "'\\n'", expression, flags=re.IGNORECASE)

        # super dangerous, also should probably be concat to handle nulls
        expression = expression.replace('&', ' || ')

        if context.dataset_name:
            expression = re.sub("\\[{}\\.([\\w.\\- _$#:/]+)]".format(
                context.dataset_name.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)').replace('[', '\\[')), '"\\1"',
                                expression, flags=re.UNICODE)
        expression = re.sub("\\[([\\w.\\- _$#:/§€Ç]+)\n*]", '"\\1"', expression, flags=re.UNICODE)
        for esri, qgis in ExpressionConverter.FUNCTION_MAP.items():
            expression = re.sub(r"{}\s*\(".format(esri), '{}('.format(qgis), expression, flags=re.IGNORECASE)

        return expression

    # pylint: disable=too-many-branches, too-many-statements, unused-argument
    @staticmethod
    def convert_python_expression(expression: str,
                                  context: Context,
                                  is_advanced: bool = False) -> str:
        """
        Rudimentary Python to QGIS expression conversion
        """
        # super dangerous!
        def convert_partial_statement(part):
            part_expression, _ = re.subn(r"(\".*?)'(.*?\")", '\\1\'\'\\2', part, flags=re.UNICODE)
            part_expression = part_expression.replace('"', "'")
            part_expression = re.sub(r"\[([^\W\d_][\w.\- _$#:]*)]", '"\\1"', part_expression, flags=re.UNICODE)

            for esri, qgis in ExpressionConverter.PYTHON_OPERATOR_MAP.items():
                part_expression = re.sub(r"(\"[a-zA-Z0-9_ ]+\")\s*\.{}\(\)".format(esri), '{}(\\1)'.format(qgis), part_expression,
                                    flags=re.IGNORECASE)
                part_expression = re.sub(r"('[^']+')\s*\.{}\(\)".format(esri), '{}(\\1)'.format(qgis), part_expression,
                                    flags=re.IGNORECASE)

            for esri, qgis in ExpressionConverter.PYTHON_FUNCTION_MAP.items():
                part_expression = re.sub(r"{}\s*\(".format(esri), '{}('.format(qgis), part_expression, flags=re.IGNORECASE)

            while True:
                match = re.search(r'(\"[a-zA-Z0-9_ ]+\")\s*\[\s*(\d*)\s*:\s*(\d*)\s*]', part_expression, flags=re.IGNORECASE)
                if not match:
                    match = re.search(r'\(\s*(\"[a-zA-Z0-9_ ]+\"\s*)\s*\)\s*\[\s*(\d*)\s*:\s*(\d*)\s*]',
                                      part_expression, flags=re.IGNORECASE)
                if match:
                    if match.group(2) and match.group(3):
                        part_expression, _ = re.subn(r'\(?\s*{}\s*\)?\s*\[\s*\d*\s*:\s*\d*\s*]'.format(match.group(1)), 'substr({}, {}, {})'.format(match.group(1).strip(), int(match.group(2)) +1, int(match.group(3)) - int(match.group(2))), part_expression)
                        continue
                    if match.group(2) and not match.group(3):
                        part_expression, _ = re.subn(r'\(?\s*{}\s*\)?\s*\[\s*\d*\s*:\s*]'.format(match.group(1)), 'substr({}, {})'.format(match.group(1).strip(), match.group(2)), part_expression)
                        continue
                    if match.group(3):
                        part_expression, _ = re.subn(r'\(?\s*{}\s*\)?\s*\[\s*:\s*\d*\s*]'.format(match.group(1)), 'left({}, {})'.format(match.group(1).strip(), match.group(3)), part_expression)
                        continue

                break

            match = re.match(r'^\s*return\s*(.*?)\s*$', part_expression, flags=re.IGNORECASE)
            if match:
                part_expression = match.group(1)

            return part_expression

        expression = expression.replace('\r\n', '\n')

        lines = expression.split('\n')
        out_lines = []
        for line in lines:
            if re.match(r'^\s*def\s+[a-zA-Z0-9_]+\s*\([ ,\w\[\]]*\s*\)\s*:\s*$', line, flags=re.IGNORECASE | re.UNICODE):
                continue
            out_lines.append(line)
        lines = out_lines
        expression = '\n'.join(lines)

        is_case = True
        case_lines = []
        idx = 0
        for line in lines:
            if not line.strip():
                continue

            if re.match(r'^\s*def\s+[a-zA-Z0-9_]+\s*\([ ,\w\[\]]*\s*\)\s*:\s*$', line, flags=re.IGNORECASE|re.UNICODE):

                continue

            if idx % 2 == 0:
                match = re.match(r'^\s*(?:el)?if (.*?)\s*(==|<>|>=|<=|>|<)\s*(.*)\s*:\s*$', line, flags=re.IGNORECASE)
                if match:
                    case_expression = convert_partial_statement( match.group(1))
                    case_result = convert_partial_statement(match.group(3))
                    if match.group(2) == '==':
                        condition = '='
                    else:
                        condition = match.group(2)
                    case_lines.append('WHEN {}{}{} THEN'.format(case_expression.strip(), condition, case_result.strip()))
                elif re.match(r'^\s*else:\s*$', line, flags=re.IGNORECASE):
                    case_lines.append('ELSE')
                else:
                    is_case = False
                    break
            else:

                if is_advanced:
                    match = re.match(r'^\s*return\s*(.*?)\s*$', line, flags=re.IGNORECASE)
                    if match:
                        line = match.group(1)
                case_lines.append(convert_partial_statement(line))
            idx += 1

        if is_case and case_lines:
            case_lines[0] = 'CASE ' + case_lines[0]

            if 'ELSE' not in case_lines:
                case_lines.append('ELSE NULL')

            case_lines.append('END')
            expression = ' '.join(case_lines)
        else:
            expression = convert_partial_statement(expression)

        return expression

    # pylint: enable=too-many-branches, too-many-statements, unused-argument

    @staticmethod
    def convert_js_expression(expression: str) -> str:
        """
        Rudimentary JS to QGIS expression conversion
        """
        # super dangerous!
        expression = re.sub("\\[([\\w.\\- _$#:]+)]", '"\\1"', expression, flags=re.UNICODE)
        return expression

    @staticmethod
    def convert_esri_sql(expression: str) -> str:
        """
        Rudimentary ESRI SQL to QGIS expression conversion
        """
        expression = re.sub("\\[([\\w.\\- _$#:]+)]", '"\\1"', expression, flags=re.UNICODE)
        expression = re.sub(r"#(\d+-\d+-\d+\s+\d+:\d+:\d+)#", "'\\1'", expression, flags=re.UNICODE)
        return expression

    @staticmethod
    def field_name_from_qgis_expression(expression: str) -> Optional[str]:
        """
        Tries to extract a field name from a QGIS expression which represents a single field reference
        """
        exp = QgsExpression(expression)
        exp.prepare(None)

        if not exp.isField():
            return None

        return exp.rootNode().name()
