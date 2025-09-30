# pylint: disable=bad-continuation,too-many-lines

"""
Test Conversion Utils
"""

import unittest

from qgis.core import QgsProject

from ..converters.context import Context
from ..converters.layout import LayoutConverter
from .test_case import SlyrTestCase


class TestLayoutConverter(SlyrTestCase):
    """
    Test Expression Conversion
    """

    def test_dynamic_text(self):
        context = Context()
        context.project = QgsProject.instance()
        self.assertEqual(LayoutConverter.convert_dynamic_text("", context), "")

        # arc pro doesn't seem to care about the >!
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="name"/abc', context
            ),
            "[% @project_title %]abc",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="name"/>', context
            ),
            "[% @project_title %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="path"/>', context
            ),
            "[% @project_path %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="folder"/>', context
            ),
            "[% @project_folder %]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="name"/>', context
            ),
            "[% @layout_name %]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="title"/>', context
            ),
            "[% coalesce(@layout_title, @layout_name) %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="tags"/>', context
            ),
            "[% @layout_tags %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="summary"/>', context
            ),
            "[% @layout_summary %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="summary"/>', context
            ),
            "[% @layout_summary %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="description"/>',
                context,
            ),
            "[% @layout_description %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="description"/>', context
            ),
            "[% @layout_description %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="credits"/>', context
            ),
            "[% @layout_credits %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="credits"/>', context
            ),
            "[% @layout_credits %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="uselimit"/>', context
            ),
            "[% @layout_constraints %]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="title" preStr="Title " newLine="true" emptyStr=""/>',
                context,
            ),
            "\nTitle [% coalesce(@layout_title, @layout_name) %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="tags" preStr="Tags " newLine="true" emptyStr=""/>',
                context,
            ),
            "\nTags [% @layout_tags %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="summary" preStr="Summary " newLine="true" emptyStr=""/>',
                context,
            ),
            "\nSummary [% @layout_summary %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="description" preStr="Description " newLine="true" emptyStr=""/>',
                context,
            ),
            "\nDescription [% @layout_description %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="credits" preStr="Credits " newLine="true" emptyStr=""/>',
                context,
            ),
            "\nCredits [% @layout_credits %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="uselimit" preStr="Constraints " newLine="true" emptyStr=""/>',
                context,
            ),
            "\nConstraints [% @layout_constraints %]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="short"/>', context
            ),
            "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="MMMM yyyy"/>', context
            ),
            "[% format_date(@project_last_saved, 'MMMM yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="yyyy"/>', context
            ),
            "[% format_date(@project_last_saved, 'yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="dd MMM yyyy"/>',
                context,
            ),
            "[% format_date(@project_last_saved, 'dd MMM yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="dd/MM/yyyy"/>',
                context,
            ),
            "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="MMMM dd, yyyy"/>',
                context,
            ),
            "[% format_date(@project_last_saved, 'MMMM dd, yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format="MMMM dd, yyyy"/>',
                context,
            ),
            "[% format_date(@project_last_saved, 'MMMM dd, yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="project" property="dateSaved" format=" "/>', context
            ),
            "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="mapFrame" name="WEBMAP_MAP_FRAME" property="sr" srProperty="datum"/>',
                context,
            ),
            "[% item_variables('WEBMAP_MAP_FRAME')['map_crs_ellipsoid']%]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                """<dyn type="mapFrame" name="Map Frame Tecno" property="sr" srProperty="name" preStr="" newLine="true" emptyStr=""/>""",
                context,
            ),
            "\n[% item_variables('Map Frame Tecno')['map_crs_description']%]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                """<dyn type="mapFrame" name="Map Frame Tecno" property="scale" pageUnits="xxxx" mapUnits="xxxx" pageValue="1" decimalPlaces="0"/>""",
                context,
            ),
            "[% format_number(item_variables('Map Frame Tecno')['map_scale'], places:=0, omit_group_separators:=true, trim_trailing_zeroes:=true) %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                """<dyn type="mapFrame" name="Map Frame Tecno" property="scale" pageUnits="xxxx" mapUnits="xxxx" pageValue="1" decimalPlaces="2"/>""",
                context,
            ),
            "[% format_number(item_variables('Map Frame Tecno')['map_scale'], places:=2, omit_group_separators:=true, trim_trailing_zeroes:=true) %]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="title" emptyStr=""/>',
                context,
            ),
            "[% coalesce(@layout_title, @layout_name) %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="contactname" emptyStr="Unavailable"/>',
                context,
            ),
            "[% coalesce(@project_author, 'Unavailable') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" property="metadata" attribute="credits" emptyStr="xxx"/>',
                context,
            ),
            "[% coalesce(array_to_string(map_credits()), 'xxx') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="layout" name="FWS_Map_D-Size_Portrait" property="serviceLayerCredits"/>',
                context,
            ),
            "[% array_to_string(map_credits()) %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                """<dyn type="layout" property="serviceLayerCredits" separator="\\n" showLayerNames="false" layerNameSeparator=": "/>""",
                context,
            ),
            "[% array_to_string(map_credits(), delimiter:='\\n') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="page" property="index"/>', context
            ),
            "[% @atlas_featurenumber %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="page" property="count"/>', context
            ),
            "[% @atlas_totalfeatures %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="page" property="number"/>', context
            ),
            "[% @atlas_featurenumber %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="page" property="name"/>', context
            ),
            "[% @atlas_pagename %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="page" property="abc"/>', context
            ),
            '[% "abc" %]',
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="date" format="month"/>', context
            ),
            "[% format_date(now(), 'MMMM, yyyy') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="date" format="dd"/>', context
            ),
            "[% format_date(now(), 'dd') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="date" format="MMMM"/>', context
            ),
            "[% format_date(now(), 'MMMM') %]",
        )
        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                '<dyn type="date" format="MM/dd/yyyy"/>', context
            ),
            "[% format_date(now(), 'MM/dd/yyyy') %]",
        )

        self.assertEqual(
            LayoutConverter.convert_dynamic_text(
                """<dyn type="project" property="dateSaved" format="|short"/>""",
                context,
            ),
            """[% format_date(@project_last_saved, 'dd/MM/yyyy') %]""",
        )

    def test_html_text(self):
        context = Context()
        context.project = QgsProject.instance()
        self.assertEqual(LayoutConverter.convert_html("", context), ("", False))
        self.assertEqual(
            LayoutConverter.convert_html('Point\r\n<FNT size="18">text</FNT>', context),
            ('Point<br>\n<span style="font-size: 18pt">text</span>', True),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                "<sub>For</sub> assistance in completing",
                context,
            ),
            (
                "<sub>For</sub> assistance in completing",
                True,
            ),
        )

        self.assertEqual(
            LayoutConverter.convert_html("<bol>The</bol> test", context),
            ("<b>The</b> test", True),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                '<FNT name="Arial" size="11"><BOL>text6</BOL></FNT>', context
            ),
            (
                '<span style="font-family: Arial; font-size: 11pt"><b>text6</b></span>',
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                '<FNT style="Bold" size="19">For assistance in completing this template, see asso<FNT size="18">ciated guide.</FNT></FNT>',
                context,
            ),
            (
                '<span style="font-weight: bold; font-size: 19pt">For assistance in '
                'completing this template, see asso<span style="font-size: 18pt">ciated '
                "guide.</span></span>",
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """<BOL><ITA><FNT name="Book Antiqua">Horton Family Maps</FNT></ITA></BOL>"""
                """<LIN leading="-4"></LIN><BOL><FNT size='40'>Greater City of Santa Fe"""
                """ </FNT></BOL><LIN leading="-6"></LIN><FNT size='27'></FNT>""",
                context,
            ),
            (
                '<b><i><span style="font-family: Book Antiqua;">Horton Family Maps</span></i></b><LIN '
                'leading="-4"></LIN><b><span style="font-size: 40pt">Greater City of Santa Fe '
                '</span></b><LIN leading="-6"></LIN><span style="font-size: 27pt"></span>',
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """<FNT name="Arial" size="8">text8</FNT> \r\n<FNT name="Arial" size="8">                                                     text8</FNT> \r\n<FNT name="Arial" size="8">text8</FNT> \r\n<FNT name="Arial" size="8">                                                     text8</FNT> """,
                context,
            ),
            (
                '<span style="font-family: Arial; font-size: 8pt">text8</span> <br>\n'
                '<span style="font-family: Arial; font-size: 8pt">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; '
                "text8</span> <br>\n"
                '<span style="font-family: Arial; font-size: 8pt">text8</span> <br>\n'
                '<span style="font-family: Arial; font-size: 8pt">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; '
                "text8</span> ",
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html("""<FNT style="Bold">WPD</FNT>""", context),
            ('<span style="font-weight: bold">WPD</span>', True),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """Ecosphère, <FNT style="Bold">WPD</FNT>""", context
            ),
            ('Ecosphère, <span style="font-weight: bold">WPD</span>', True),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """Ecosphère, <FNT style="Bold">WPD</FNT>, [% format_date(now(), 'MMMM, yyyy') %]""",
                context,
            ),
            (
                """Ecosphère, <span style=\"font-weight: bold\">WPD</span>, [% format_date(now(), 'MMMM, yyyy') %]""",
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """<LIN leading = "2"><FNT name="Arial" size = "10">Carte 1</FNT>\nLocalisation du site</LIN>""",
                context,
            ),
            (
                '<div style="margin-top: 2.0pt">&#8203;</div><span style="font-family: Arial; '
                'font-size: 10pt">Carte 1</span><br>\n'
                "Localisation du site",
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """<FNT style="Italic">Les Sables Olimag inc.\n</FNT>Caractérisation des milieux naturels de l’ancien\nsite minier Frontenac\nProgramme de travail préliminaire""",
                context,
            ),
            (
                '<span style="font-style: italic">Les Sables Olimag inc.<br>\n</span>Caractérisation des milieux naturels de l’ancien<br>\nsite minier Frontenac<br>\nProgramme de travail préliminaire',
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """<LIN leading="1.5">Les Sables Olimag inc.\n</LIN><LIN leading="1.5">Caractérisation des milieux naturels de l’ancien\n</LIN>site minier Frontenac\nProgramme de travail préliminaire""",
                context,
            ),
            (
                '<div style="margin-top: 1.5pt">&#8203;</div>Les Sables Olimag inc.<br>\n'
                '<div style="margin-top: 1.5pt">&#8203;</div>Caractérisation des milieux '
                "naturels de l’ancien<br>\n"
                "site minier Frontenac<br>\n"
                "Programme de travail préliminaire",
                True,
            ),
        )
        self.assertEqual(
            LayoutConverter.convert_html(
                """<FNT style="Italic"><LIN leading="1.5">Les Sables Olimag inc.\n</LIN></FNT><LIN leading="1.5">Caractérisation des milieux naturels de l’ancien\n</LIN>site minier Frontenac\nProgramme de travail préliminaire""",
                context,
            ),
            (
                '<span style="font-style: italic"><div style="margin-top: '
                '1.5pt">&#8203;</div>Les Sables Olimag inc.<br>\n'
                '</span><div style="margin-top: 1.5pt">&#8203;</div>Caractérisation des '
                "milieux naturels de l’ancien<br>\n"
                "site minier Frontenac<br>\n"
                "Programme de travail préliminaire",
                True,
            ),
        )

        self.assertEqual(
            LayoutConverter.convert_html(
                """<LINK>http://google.com</LINK> test links <link>https://test.com</link>aaa""",
                context,
            ),
            (
                '<a href="http://google.com" style="text-decoration: none">http://google.com</a> test links <a href="https://test.com" style="text-decoration: none">https://test.com</a>aaa',
                True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
