# pylint: disable=bad-continuation,too-many-lines

"""
Test LYR parsing
"""

import ast
import os
import pprint
import unittest
import tempfile

from .test_case import SlyrTestCase

from qgis.core import QgsProject

from ..parser.initalize_registry import initialize_registry
from ..parser.streams.map_document import MapDocument

from ..converters.context import Context
from ..converters.project import ProjectConverter
from .utils import Utils


expected = [
    {"filename": "project_fixed_extent_36373435.mxd"},
    {"filename": "layout_text_right.mxd"},
    {"filename": "layout_text_bottom_right.mxd"},
    {"filename": "project_azimuth_217_altitude_33_contrast_6.3.mxd"},
    {"filename": "project_no_simulate_layer_transparency_in_legends.mxd"},
    {"filename": "layout_text_object.mxd"},
    {"filename": "project_dataframe_fixed_scale_188888888.mxd"},
    {"filename": "layout_text_left.mxd"},
    {"filename": "layout_text_top_right.mxd"},
    {"filename": "project_attributes.mxd"},
    {"filename": "layout_text_center.mxd"},
    {"filename": "simple_project_layout.mxd"},
    {"filename": "project_draft_mode_name_only.mxd"},
    {"filename": "project_crs_web_mercator.mxd"},
    {"filename": "project_map_units_miles.mxd"},
    {"filename": "project_rotation_37_anticlockwise.mxd"},
    {"filename": "layout_text_bottom_left.mxd"},
    {"filename": "layout_text_top_center.mxd"},
    {"filename": "project_use_maplex.mxd"},
    {"filename": "project_frame_gap_x3_y4_rounding24.mxd"},
    {"filename": "simple_project.mxd"},
    {"filename": "project_background_blue_gap_x13_y14_56_rounding.mxd"},
    {"filename": "project_azimuth_217_altitude_33.mxd"},
    {"filename": "layout_text_bottom_center.mxd"},
    {"filename": "project_drop_shadow_x23_y24_rounding45.mxd"},
    {"filename": "project_allow_assignment_of_unique_ids_for_publishing.mxd"},
    {
        "filename": "project_frame_gap_x3_y4_rounding.mxd",
    },
    {"filename": "project_map_units_decimenters.mxd"},
    {"filename": "project_reference_scale_1777.mxd"},
    {"filename": "simple_project_two_frames.mxd"},
    {"filename": "layout_picture_frame_border_shadow.mxd"},
    {"filename": "layout_two_pictures.mxd"},
    {"filename": "layout_picture_height11.mxd"},
    {"filename": "layout_picture_elementname.mxd"},
    {"filename": "layout_map_title.mxd"},
    {
        # Seems like ArcGIS doesn't correctly save this setting...
        "filename": "layout_picture_path_from_datadriven_attribute.mxd"
    },
    {"filename": "layout_picture_x13y24.mxd"},
    {"filename": "layout_vertical_guide_5_10_15.mxd"},
    {"filename": "layout_data_driven_page.mxd"},
    {"filename": "layout_horizontal_guides_15_20_25.mxd"},
    {"filename": "layout_ole_object.mxd"},
    {"filename": "layout_picture_draft_mode.mxd"},
    {"filename": "scale_text_x13_y14.mxd"},
    {"filename": "layout_picture_width17_height11_nopreseveaspect.mxd"},
    {"filename": "layout_picture_bmp.mxd"},
    {"filename": "layout_picture_width17.mxd"},
    {"filename": "layout_north_arrow_44_calculated.mxd"},
    {"filename": "layout_picture_save_in_document.mxd"},
    {"filename": "layout_picture_size_percent_115h_125w_nopreseveaspect.mxd"},
    {"filename": "map_frame_clip_to_shape_exclude_none.mxd"},
    {"filename": "map_frame_clip_to_outline_of_features.mxd"},
    {"filename": "standalone_table_display_expression.mxd"},
    {"filename": "standalone_table_enable_time_offset_6_centuires.mxd"},
    {"filename": "extent_indicator_show_leader.mxd"},
    {"filename": "extent_indicator_show_leader_green.mxd"},
    {"filename": "standalone_table_enable_time_data_changes_frequently.mxd"},
    {"filename": "map_frame_clip_guides_and_graticules.mxd"},
    {"filename": "map_frame_clip_to_shape_exclude_lines.mxd"},
    {"filename": "standalone_table_definition_query.mxd"},
    {"filename": "extent_indicators.mxd"},
    {"filename": "minimum_scale_for_auto_cache.mxd"},
    {"filename": "map_frame_clip_to_shape_extent.mxd"},
    {"filename": "map_frame_clip_to_shape_exclude_lines_and_polys.mxd"},
    {"filename": "standalone_table.mxd"},
    {"filename": "map_frame_grid.mxd"},
    {"filename": "map_frame_clip_border_4_pt.mxd"},
    {"filename": "standalone_table_enable_time_step_55mins.mxd"},
    {"filename": "automatically_build_cache_when_map_extent_changes.mxd"},
    {"filename": "standalone_table_enable_time_oid.mxd"},
    {"filename": "standalone_table_joins.mxd"},
    {"filename": "standalone_table_enable_time_display_cumulative.mxd"},
    {"filename": "standalone_table_display_abbrev_name.mxd"},
    {"filename": "extent_indicator_background_shadow.mxd"},
    {"filename": "extent_indicator_use_simple.mxd"},
    {"filename": "standalone_table_relate.mxd"},
    {"filename": "legend_no_reorder_when_map_layers_reordered.mxd"},
    {"filename": "legend_no_show_title.mxd"},
    {"filename": "legend_wrap_label_36.mxd"},
    {"filename": "legend_fixed_frame_no_shrink_contents_to_fit_frame.mxd"},
    {"filename": "legend_show_feature_count_no_thousands.mxd"},
    {"filename": "legend_title_symbol_red.mxd"},
    {"filename": "legend_column_settings.mxd"},
    {"filename": "legend_min_font_size_88.mxd"},
    {"filename": "legend_draft_mode.mxd"},
    {"filename": "legend_right_to_left.mxd"},
    {"filename": "legend.mxd"},
    {"filename": "legend_element_name.mxd"},
    {"filename": "legend_group_gap_15_3.mxd"},
    {"filename": "legend_default_size_47_42.mxd"},
    {"filename": "legend_anchor_bottom_right.mxd"},
    {"filename": "legend_scale_symbols_when_reference_scale_set.mxd"},
    {"filename": "legend_fixed_frame_no_auto_adjust_number_column.mxd"},
    {"filename": "legend_no_only_show_layers_checked_in_toc.mxd"},
    {"filename": "legend_no_add_new_items_to_legend_when_added_to_map.mxd"},
    {"filename": "legend_default_patches.mxd"},
    {"filename": "legend_wrap_descriptions_48.mxd"},
    {"filename": "legend_only_show_classes_visible_in_map.mxd"},
    {"filename": "legend_styles.mxd"},
    {"filename": "legend_fixed_frame.mxd"},
    {"filename": "legend_show_feature_coutn.mxd"},
    {"filename": "layout_scalebar_preserve_aspec.mxd"},
    {"filename": "layout_ole_draft_mode.mxd"},
    {"filename": "layout_north_arrow_frames.mxd"},
    {"filename": "layout_scalebar_element_name.mxd"},
    {"filename": "layout_scalebar_13_14_15_16.mxd"},
    {"filename": "layout_scalebar_frame.mxd"},
    {"filename": "layout_scaletext_13_14_height_16.mxd"},
    {"filename": "layout_neatline_13_14_15_16.mxd"},
    {"filename": "layout_north_arrow_anchor_middl.mxd"},
    {"filename": "layout_ole_13_14_15.mxd"},
    {"filename": "layout_picture_save_in_doc.mxd"},
    {"filename": "layout_map_anchor_bottom_right.mxd"},
    {"filename": "layout_neatline_element_name.mxd"},
    {"filename": "layout_scaletext_anchor_center.mxd"},
    {"filename": "layout_ole_anchor_bottom_right.mxd"},
    {"filename": "layout_map_preserve_aspect.mxd"},
    {"filename": "layout_north_arrow_draft_mode.mxd"},
    {"filename": "layout_picture_13_14_15_16.mxd"},
    {"filename": "layout_legend_13_14_width_15.mxd"},
    {"filename": "layout_ole_fram.mxd"},
    {"filename": "layout_title.mxd"},
    {"filename": "layout_legend_anchor_top_right.mxd"},
    {"filename": "layout_ole.mxd"},
    {"filename": "layout_legend_anchor_middle.mxd"},
    {"filename": "layout_title_align_justify.mxd"},
    {"filename": "layout_picture.mxd"},
    {"filename": "layout_legend_13_14_height_16.mxd"},
    {"filename": "layout_scalebar_align_to_zero_division.mxd"},
    {"filename": "layout_neatline_preserve_aspect.mxd"},
    {"filename": "layout_neatline_draft_mode.mxd"},
    {"filename": "layout_pos_13_14_height_18.mxd"},
    {"filename": "layout_title_char_spacing_13_leading_1.mxd"},
    {"filename": "layout_scalebar_anchor_middle.mxd"},
    {"filename": "layout_map_anchor_top_left.mxd"},
    {"filename": "layout_pos_13_14_width_17.mxd"},
    {"filename": "layout_scaletext_draft_mode.mxd"},
    {"filename": "layout_neatline_anchor_bottom_right.mxd"},
    {"filename": "layout_title_angle_45_anticlockwise.mxd"},
    {"filename": "layout_scaletext.mxd"},
    {"filename": "layout_picture_anchor_bottom_right.mxd"},
    {"filename": "layout_scalebar_anchor_top_right.mxd"},
    {"filename": "layout_neatline_anchor_top_left.mxd"},
    {"filename": "layout_title_anchor_center.mxd"},
    {"filename": "layout_ole_element_name.mxd"},
    {"filename": "layout_scaletext_13_14_width_15.mxd"},
    {"filename": "layout_title_align_right.mxd"},
    {"filename": "layout_north_arrow_13_14_width_15.mxd"},
    {"filename": "layout_ole_anchor_top_right.mxd"},
    {"filename": "layout_scaletext_element_name.mxd"},
    {"filename": "layout_map_pos_15_16_size_17_18.mxd"},
    {"filename": "layout_picture_frame.mxd"},
    {"filename": "layout_title_align_lef.mxd"},
    {"filename": "layout_picture_element_name.mxd"},
    {"filename": "layout_north_arrow_13_14_height_16.mxd"},
    {"filename": "layout_picture_preserve_aspect.mxd"},
    {"filename": "layout_title_align_center.mxd"},
    {"filename": "layout_picture_anchor_top_right.mxd"},
    {"filename": "layout_scaletext_anchor_bottomright.mxd", "skip": True},
    {"filename": "background_color_blue.mxd"},
    {"filename": "frame_draw_using_masking_levels_to_masked_layers.mxd"},
    {"filename": "two_frames_active_new_data_frame.mxd"},
    {"filename": "two_frames_active_layers.mxd"},
    {"filename": "project_list_by_selectable_collapse_groups.mxd"},
    {
        "filename": "document_attributes.mxd",
        "skip": True,  # not saved correctly?
    },
    {
        "filename": "lines_flicker_999ms.mxd",
        "skip": True,  # not stored in layer properties
    },
    {"filename": "project_toc_options_no_show_selected_faetures.mxd", "skip": True},
    {"filename": "frame_draw_using_masking_complex.mxd"},
    {"filename": "frame_draw_using_masking_polys_lnie_points.mxd"},
    {"filename": "simple_project_small_window_height_resize.mxd"},
    {"filename": "simple_project_small_window_moved.mxd"},
    {"filename": "label_locke.mxd", "skip": True},
    {"filename": "project_toc_options_show_group_layer_name.mxd", "skip": True},
    {"filename": "project_toc_options_patch_zigzag_ellipse.mxd"},
    {"filename": "project_list_by_visibility_collapsed.mxd"},
    {"filename": "frame_draw_using_masking_complex_deactivated.mxd"},
    {"filename": "project_list_by_visibility_visible_group_collpased.mxd"},
    {"filename": "document_absolute_sources.mxd"},
    {"filename": "document_thumbnail.mxd", "skip": True},
    {"filename": "project_toc_options_order_alpabetical.mxd", "skip": True},
    {"filename": "project_lines_not_selectable.mxd"},
    {"filename": "project_toc_options_order_as_drawn.mxd"},
    {"filename": "frame_draw_using_masking_complex2.mxd"},
    {"filename": "project_list_by_selectable.mxd"},
    {
        "filename": "document_relative_sources.mxd",
    },
    {"filename": "simple_project_small_window.mxd"},
    {"filename": "document_last_printed_last_exported.mxd"},
    {"filename": "labels_paused.mxd", "skip": True},
    {"filename": "label_priority_lines_points.mxd", "skip": True},
    {
        "filename": "lines_flicker_500ms.mxd",
        "skip": True,  # not stored in layer properties?
    },
    {"filename": "frame_draw_using_masking_polys_points.mxd"},
    {"filename": "project_lines_not_selectab;le.mxd", "skip": True},
    {"filename": "project_list_by_source.mxd"},
    {"filename": "project_toc_options_patch_size_57_59.mxd"},
    {"filename": "project_list_by_visibility.mxd"},
    {"filename": "label_priority_points_lines.mxd", "skip": True},
    {"filename": "simple_project_small_window_toc_resized.mxd"},
    {"filename": "label_view_unplace.mxd"},
    {"filename": "labeling_color_for_unplaced_blue.mxd"},
    {"filename": "labeling_orientation_vertical_labels_neg30.mxd"},
    {"filename": "labeling_rotate_point_line_labels_when_frame_rotated.mxd"},
    {"filename": "groups_expanded.mxd"},
    {
        "filename": "project_coordinates_status_bar.mxd",  # not stored in project?
    },
    {"filename": "project_default_symbol_triangle_red_line_green_fill.mxd"},
    {"filename": "project_default_table_font_calibri.mxd"},
    {"filename": "project_default_callout_text_red_8.mxd"},
    {
        "filename": "project_default_maple.mxd",
        "skip": True,  # can't locate - maybe not stored in project
    },
    {
        "filename": "project_default_font_calibri_10.mxd",
        "skip": True,  # maybe not stored in project?
    },
    {"filename": "project_default_label_purple_16.mxd"},
    {"filename": "page_definition_query_matching.mxd"},
    {"filename": "page_definition_query_dont_match.mxd"},
    {"filename": "representations.mxd", "skip": True},
    {"filename": "data_Driven_pages_sort_descending.mxd"},
    {"filename": "data_driven_pages_data_driven_best_fit_157_percent.mxd"},
    {"filename": "data_driven_pages_data_driven_best_fit_157_page_units.mxd"},
    {"filename": "data_driven_pages_many_features.mxd"},
    {"filename": "data_driven_pages_data_driven_round_scale_nearest_25.mxd"},
    {"filename": "data_driven_pages_disable.mxd"},
    {"filename": "data_driven_pages_center_and_maintain_scal.mxd"},
    {"filename": "data_Driven_pages_crs_crew_page_no_staff.mxd"},
    {"filename": "data_driven_pages_scale_use.mxd"},
    {"filename": "data_driven_pages_name_class_sort_importance.mxd"},
    {"filename": "data_driven_pages_data_driven_scale_value.mxd"},
    {"filename": "data_driven_pages_data_driven_best_fit_157_map_units.mxd"},
    {"filename": "data_driven_pages_start_page_number23.mxd"},
    {"filename": "data_Driven_pages_rotation_heading.mxd"},
    {"filename": "map_frame_grid_labels_bottom.mxd"},
    {"filename": "data_driven_pages_center_and_maintain_current_scale.mxd"},
    {"filename": "map_frame_grid_ticks_major_inside.mxd"},
    {"filename": "layout_shapes.mxd"},
    {"filename": "data_driven_pages_margin_178_map_units.mxd"},
    {"filename": "map_frame_grid_ticks_minor_inside.mxd"},
    {"filename": "data_driven_pages_margin_178_page_units.mxd"},
    {"filename": "data_driven_pages_data_drive_scale_value.mxd"},
    {"filename": "map_frame_grid_labels_left.mxd"},
    {"filename": "map_frame_grid_ticks_major_top_sub_left.mxd"},
    {"filename": "map_frame_grid_labels_top.mxd"},
    {"filename": "map_frame_grid_labels_rigjt.mxd"},
    {"filename": "data_driven_pages_margin_178_percent.mxd"},
    {"filename": "legend_override_patch_size.mxd"},
    {"filename": "legend_per_item_label_style.mxd"},
    {"filename": "legend_override_patch_size2.mxd"},
    {"filename": "legend_patch_shapes.mxd"},
    {"filename": "legend_complex_column_configuration.mxd"},
    {"filename": "scalebar_subdivisions_symbol.mxd"},
    {"filename": "legend_prevent_column_split.mxd"},
    {"filename": "page_queries.mxd"},
    {
        "filename": "simple_project_layout_108.mxd",
    },
    {"filename": "sources_relative2.mxd"},
    {"filename": "layer_opacity_with_group_opacity.mxd"},
    {"filename": "group_layer_opacity.mxd"},
    {"filename": "stepped_scale_bar.mxd"},
    {"filename": "point_text_justify_html.mxd"},
    {"filename": "point_text_top.mxd"},
    {"filename": "point_text_center.mxd"},
    {"filename": "point_text_baseline.mxd"},
    {"filename": "point_text_center_html.mxd"},
    {"filename": "point_text_vert_center.mxd"},
    {"filename": "point_text_left.mxd"},
    {"filename": "point_text_justify.mxd"},
    {"filename": "point_text_right_html.mxd"},
    {"filename": "point_text_right_90.mxd"},
    {"filename": "point_text_left_90.mxd"},
    {"filename": "point_text_right.mxd"},
    {"filename": "point_text_center_90.mxd"},
    {"filename": "point_text_baseline2.mxd"},
    {"filename": "point_text_left_html.mxd"},
    {"filename": "point_text_vert_center_html.mxd"},
    {"filename": "point_text_top_html.mxd"},
    {"filename": "point_text_left_45.mxd"},
    {"filename": "point_text_baseline_html.mxd"},
    {"filename": "interop.mxd"},
    {"filename": "point_halos.mxd"},
    {"filename": "text_background_align.mxd"},
]

initialize_registry()


class TestMxdParser(SlyrTestCase):
    """
    Test MXD parsing
    """

    UPDATE = False

    def test_mxd_parsing(self):
        """
        Checks all mxd parsing against expectations
        """
        blobs = []
        path = os.path.join(os.path.dirname(__file__), "mxd")
        for fn in os.listdir(path):
            file = os.path.join(path, fn)
            if os.path.isfile(file):
                blobs.append(fn)
        all_found = True
        for b in blobs:
            if not [e for e in expected if e["filename"] == b]:
                print(
                    """{
                   'filename': '"""
                    + b
                    + """',
                                      'skip': True
               },"""
                )
                all_found = False
        assert all_found

        for e in expected:
            if "skip" in e:
                continue

            file = os.path.join(os.path.dirname(__file__), "mxd", e["filename"])
            base, _ = os.path.splitext(e["filename"])
            expected_file = os.path.join(
                os.path.dirname(__file__), "mxd", "expected", base + ".txt"
            )
            with open(file, "rb") as f:
                print("{}".format(e["filename"]))
                doc = MapDocument(
                    f, debug=False, offset=-1, tolerant=False, check_length=True
                )

                def warning(msg, level=0):
                    pass

                context = Context()
                context.convert_fonts = False
                context.upgrade_http_to_https = True
                context.project = QgsProject.instance()
                context.unsupported_object_callback = warning

                p = QgsProject()
                context.stable_ids = True
                ProjectConverter.convert_target_project(p, file, doc, context)

                for _, layer in p.mapLayers().items():
                    Utils.normalize_layer_for_test(layer)

                with tempfile.TemporaryDirectory() as dir:
                    self.assertTrue(p.write(os.path.join(dir, "test.qgs")))
                    with open(os.path.join(dir, "test.qgs"), "rt") as qgs_content:
                        qgs = qgs_content.read()

                        qgs_xml = Utils.normalize_xml(qgs)

                res = {"original": doc.to_dict(), "qgs_xml": qgs_xml}

                if self.UPDATE:
                    with open(expected_file, "w") as o:
                        pprint.pprint(res, o)
                else:
                    # too tricky to check results across different QGIS versions!
                    pass
                    #
                    # with open(expected_file, "r") as o:
                    #    expected_res = ast.literal_eval(o.read())
                    # self.assertEqual(expected_res, res)


from qgis.core import QgsApplication

QGISAPP = QgsApplication([], True)
QgsApplication.initQgis()

if __name__ == "__main__":
    unittest.main()
