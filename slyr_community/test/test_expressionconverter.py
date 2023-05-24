# pylint: disable=bad-continuation,too-many-lines

"""
Test Conversion Utils
"""

import unittest

from ..converters.context import Context
from ..converters.expressions import ExpressionConverter


class TestExpressionConverter(unittest.TestCase):
    """
    Test Expression Conversion
    """

    def test_qgis_expression_to_field(self):
        """
        Test getting field name from qgis expression
        """
        self.assertIsNone(
            ExpressionConverter.field_name_from_qgis_expression(''))
        self.assertIsNone(
            ExpressionConverter.field_name_from_qgis_expression('1+2'))
        self.assertEqual(
            ExpressionConverter.field_name_from_qgis_expression('"my field"'),
            'my field')
        self.assertEqual(
            ExpressionConverter.field_name_from_qgis_expression('my_field'),
            'my_field')

    def test_python(self):
        """
        Test Python expression conversion
        """
        context = Context()
        self.assertEqual(
            ExpressionConverter.convert_python_expression('', context), '')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('[a field]',
                                                          context),
            '"a field"')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('[A_field123]',
                                                          context),
            '"A_field123"')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('[a field].lower()',
                                                          context),
            'lower("a field")')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('[a field].upper()',
                                                          context),
            'upper("a field")')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('len([a field])',
                                                          context),
            'length("a field")')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('len("a value")',
                                                          context),
            'length(\'a value\')')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('[a field].title()',
                                                          context),
            'title("a field")')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('[a field] .title()',
                                                          context),
            'title("a field")')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('"abc"', context),
            '\'abc\'')
        self.assertEqual(
            ExpressionConverter.convert_python_expression('"abc".title()',
                                                          context),
            'title(\'abc\')')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            'if [a field] == "NR":\n\treturn [nature].title()\nelse:\n\treturn [other].title()',
            context, is_advanced=True),
            'CASE WHEN "a field"=\'NR\' THEN title("nature") ELSE title("other") END', )
        self.assertEqual(ExpressionConverter.convert_python_expression(
            'if [a field] <> "NR":\n\treturn [nature].title()\nelse:\n\treturn [other].title()',
            context, is_advanced=True),
            'CASE WHEN "a field"<>\'NR\' THEN title("nature") ELSE title("other") END', )
        self.assertEqual(ExpressionConverter.convert_python_expression(
            'if [a field] == "NR":\n\treturn [nature].title()\nelse:\n\treturn [other].title()\n\t\n\n',
            context, is_advanced=True),
            'CASE WHEN "a field"=\'NR\' THEN title("nature") ELSE title("other") END', )
        self.assertEqual(ExpressionConverter.convert_python_expression(
            'if [a field] == "NR":\n\treturn [nature].title()\nelif [a field]=="S r 13":\n\rreturn "a value"\nelse:\n\treturn [other].title()',
            context, is_advanced=True),
            'CASE WHEN "a field"=\'NR\' THEN title("nature") WHEN "a field"=\'S r 13\' THEN \'a value\' ELSE title("other") END', )
        self.assertEqual(ExpressionConverter.convert_python_expression(
            'def SomeFunction([a field], [aANOTHER FIELD] ):\nif [a field] == "NR":\n\treturn [nature].title()\nelse:\n\treturn [other].title()',
            context, is_advanced=True),
            'CASE WHEN "a field"=\'NR\' THEN title("nature") ELSE title("other") END', )
        self.assertEqual(ExpressionConverter.convert_python_expression(
            'def FindLabel ([toponyme],[nature] ):\n\tif [a field] == "NR":\n\t\treturn [nature].title()\n\telse:\n\t\treturn [other].title()',
            context, is_advanced=True),
            'CASE WHEN "a field"=\'NR\' THEN title("nature") ELSE title("other") END', )
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ( [toponyme], [nature]  ):\r\n  if [toponyme] <>'NR':\r\n   return [toponyme].title()\r\n  else:\r\n   return [nature].title()",
            context, is_advanced=True),
            'CASE WHEN "toponyme"<>\'NR\' THEN title("toponyme") ELSE title("nature") END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\n  if [toponyme] == \"NR\":  \r\n   return [nature].title()  \r\n  else:  \r\n    return [toponyme].title()  \r\n  ",
            context, is_advanced=True),
            'CASE WHEN "toponyme"=\'NR\' THEN title("nature") ELSE title("toponyme") END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\n  if [cpx_numero]>5:  \r\n   return [cpx_numero]\r\n  ",
            context, is_advanced=True),
            'CASE WHEN "cpx_numero">5 THEN "cpx_numero" ELSE NULL END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\n  if [cpx_numero]<5:  \r\n   return [cpx_numero]\r\n  ",
            context, is_advanced=True),
            'CASE WHEN "cpx_numero"<5 THEN "cpx_numero" ELSE NULL END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\n  if [cpx_numero]<=5:  \r\n   return [cpx_numero]\r\n  ",
            context, is_advanced=True),
            'CASE WHEN "cpx_numero"<=5 THEN "cpx_numero" ELSE NULL END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\n  if [cpx_numero]>=5:  \r\n   return [cpx_numero]\r\n  ",
            context, is_advanced=True),
            'CASE WHEN "cpx_numero">=5 THEN "cpx_numero" ELSE NULL END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\n  if len( [cpx_numero] )<5:  \r\n   return [cpx_numero]\r\n  ",
            context, is_advanced=True),
            'CASE WHEN length( "cpx_numero" )<5 THEN "cpx_numero" ELSE NULL END')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\nreturn [NUMERO] [4:]\r\n  ",
            context, is_advanced=True), 'substr("NUMERO", 4)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\nreturn ([NUMERO]) [4:]\r\n  ",
            context, is_advanced=True), 'substr("NUMERO", 4)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\nreturn [NUMERO] [:4]\r\n  ",
            context, is_advanced=True), 'left("NUMERO", 4)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\nreturn ( [NUMERO] )[:4]\r\n  ",
            context, is_advanced=True), 'left("NUMERO", 4)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\nreturn [NUMERO] [1:4]\r\n  ",
            context, is_advanced=True), 'substr("NUMERO", 2, 3)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([toponyme],[nature] ):  \r\nreturn ( [NUMERO] ) [1:4]\r\n  ",
            context, is_advanced=True), 'substr("NUMERO", 2, 3)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "\"Chat. d'eau\"", context), '\'Chat. d\'\'eau\'')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([GlobalId] ):  \r\n    return ([GlobalId])[1:9]   ",
            context, is_advanced=True),
            'substr("GlobalId", 2, 8)')
        self.assertEqual(ExpressionConverter.convert_python_expression(
            "def FindLabel ([GlobalId] ):  \r\n    return (  [GlobalId]  )[1:9]   \r\n    ",
            context, is_advanced=True),
            'substr("GlobalId", 2, 8)')

    def test_sql(self):
        """
        Test SQL expression conversion
        """

        self.assertEqual(ExpressionConverter.convert_esri_sql(
            "[a field]"), '"a field"')

    def test_esri(self):
        """
        Test ESRI expression conversion
        """

        context = Context()
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[]", context), '')

        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[a field]", context), '"a field"')
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[§_Schutz]", context), '"§_Schutz"')
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[ESTA€ÇO]", context), '"ESTA€ÇO"')
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[a field] & Chr(13) & [b field]", context),
            '''"a field"  ||  '\n'  ||  "b field"''')
        context.dataset_name = 'Streams'
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[Streams.WC_LLID_NR]", context), '"WC_LLID_NR"')
        context.dataset_name = 'Rivers, Streams'
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[Rivers, Streams.WC_LLID_NR]", context), '"WC_LLID_NR"')
        context.dataset_name = 'Rivers[ Streams'
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[WC_LLID_NR]", context), '"WC_LLID_NR"')
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[NAME\n]", context), '"NAME"')
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[NAME\r\n]", context), '"NAME"')
        self.assertEqual(ExpressionConverter.convert_esri_expression(
            "[NAME\r]", context), '"NAME"')

    def test_vbscript(self):
        """
        Test Vbscript expression conversion
        """

        context = Context()
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[]", context), '')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[a field]", context), '"a field"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[Id]", context), '"Id"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[Id]", context), '"Id"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[§_Schutz]", context), '"§_Schutz"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[ESTA€ÇO]", context), '"ESTA€ÇO"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[NAME\r]", context), '"NAME"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[NAME\r\n]", context), '"NAME"')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[]", context), '')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "Left( [ADMINAREAN] , 5)", context), 'left( "ADMINAREAN" , 5)')

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "mid([MASSNAHME.MAS_NR], 5)", context),
            'substr("MASSNAHME.MAS_NR", 5)')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "mid([MASSNAHME.MAS_NR], 5, 2)", context),
            'substr("MASSNAHME.MAS_NR", 5, 2)')

        # self.assertEqual(ExpressionConverter.convert_vbscript_expression(
        #    '''"''" & [BLOCK_NUM] & "''"''', context),
        #                 """''\\''  ||  "BLOCK_NUM"  ||  '\\'\\''""")

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "instr( [ADMINAREAN] , 'a')", context),
            'strpos( "ADMINAREAN" , \'a\')')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "instr( [ADMINAREAN] , 'ab' )", context),
            'strpos( "ADMINAREAN" , \'ab\' )')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "instr( [ADMINAREAN] , \"a\")", context),
            'strpos( "ADMINAREAN" , \'a\')')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "instr( [ADMINAREAN] , \"ab\" )", context),
            'strpos( "ADMINAREAN" , \'ab\' )')
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[Name] & vbNewLine & \"Pop: \" & FormatNumber ([POP_2000],0 )",
            context),
            '"Name"  ||  \'\n\'  ||  \'Pop: \'  ||  format_number("POP_2000",0 )')
        # not supported!
        # self.assertEqual(ExpressionConverter.convert_vbscript_expression(
        #    "instr(55, [ADMINAREAN] , 'ab' )", context), 'strpos( "ADMINAREAN" , \'ab\')')

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "Left( [ADMINAREAN] , Instr( [ADMINAREAN] ,\",\")-1)", context),
            'left( "ADMINAREAN" , strpos( "ADMINAREAN" ,\',\')-1)')

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            '''"<BOL>" & [MapUnit] & "</BOL>" &  vbNewLine  & "<FNT size = '6'>" &  [PolyNumber] & "</FNT>"''',
            context),
            """'<BOL>'  ||  "MapUnit"  ||  '</BOL>'  ||   '\n'   ||  '<FNT size = \\'6\\'>'  ||   "PolyNumber"  ||  '</FNT>'""")

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            '''"<BOL>" & [MapUnit] & "</BOL>" &  vbNewLine  & "<FNT name = 'Arial' size = '6'>" &  [PolyNumber] & "</FNT>"''',
            context),
            """'<BOL>'  ||  "MapUnit"  ||  '</BOL>'  ||   '\n'   ||  '<FNT name = \\'Arial\\' size = \\'6\\'>'  ||   "PolyNumber"  ||  '</FNT>'""")

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            '''[MINE_NAME] & vbnewline & int([Hectares] ) & " Ha"''', context),
            '''"MINE_NAME"  ||  \'\n\'  ||  to_int("Hectares" )  ||  \' Ha\'''')

        self.assertEqual(
            ExpressionConverter.convert_vbscript_expression('"\' "', context),
            "'\\' '")
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            '''[WIDTH] &"' " & [Easement_Type] &chr(13)& [LIBER] &"/"& [PAGE] &chr(13)& [Comment_Label]''',
            context),
            '''"WIDTH"  || \'\\\' \'  ||  "Easement_Type"  || \'\\n\' ||  "LIBER"  || \'/\' ||  "PAGE"  || \'\\n\' ||  "Comment_Label"'''
        )

        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            """left([NOME] ,instr([NOME] ," ")) & vbnewline & right( [NOME] ,len( [NOME] )-(instr([NOME] ," ")))""",
            context),
            '''left("NOME" ,strpos("NOME" ,' '))  ||  \'\n\'  ||  right( "NOME" ,length( "NOME" )-(strpos("NOME" ,' ')))''')

        context.dataset_name = 'Streams'
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[Streams.WC_LLID_NR]", context), '"WC_LLID_NR"')
        context.dataset_name = 'Rivers, Streams'
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[Rivers, Streams.WC_LLID_NR]", context), '"WC_LLID_NR"')
        context.dataset_name = 'Rivers[ Streams'
        self.assertEqual(ExpressionConverter.convert_vbscript_expression(
            "[WC_LLID_NR]", context), '"WC_LLID_NR"')


if __name__ == '__main__':
    unittest.main()
