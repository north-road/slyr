# pylint: disable=bad-continuation,too-many-lines

"""
Test LYR parsing
"""

import unittest
import os
import pprint
import ast

from ..parser.initalize_registry import initialize_registry
from ..parser.streams.layer import LayerFile

expected = [
    {
        'filename': 'field_formats.lyr'
    },
    {
        'filename': 'lines.lyr'
    },
    {
        'filename': 'lines_gdb.lyr'
    },
    {
        'filename': 'lines2_gdb.lyr'
    },
    {
        'filename': 'legend_properties.lyr'
    },
    {
        'filename': 'invisible.lyr'
    },
    {
        'filename': '750kto33mil.lyr'
    },
    {
        'filename': '750ktonone.lyr'
    },
    {
        'filename': 'visible_none_to_none.lyr',
    },
    {
        'filename': 'lines_categorized.lyr'
    },
    {
        'filename': 'unique_reverse_sorting.lyr'
    },
    {
        'filename': 'unique_values_many_headings.lyr'
    },
    {
        'filename': 'unique_3_fields.lyr'
    },
    {
        'filename': 'label_default.lyr'
    },
    {
        'filename': 'label_chiller_28.lyr'
    },
    {
        'filename': 'label_chiller_28_bold_red.lyr'
    },
    {
        'filename': 'layer_v17.lyr'
    },
    {
        'filename': 'layer_v17b.lyr'
    },
    {
        'filename': 'layer_v17c.lyr'
    },
    {
        'filename': 'layer_v22.lyr'
    },
    {
        'filename': 'no_connection.lyr'
    },
    {
        'filename': 'label_allcaps.lyr'
    },
    {
        'filename': 'label_charspacing17_leading18_flipangle90_charwidth103_wordspace107.lyr'
    },
    {
        'filename': 'label_nokern.lyr'
    },
    {
        'filename': 'label_right_to_left.lyr'
    },
    {
        'filename': 'label_shadow_blue_xoffset13_yosffset14.lyr'
    },
    {
        'filename': 'label_smallcaps.lyr'
    },
    {
        'filename': 'label_subscript.lyr'
    },
    {
        'filename': 'label_superscript.lyr'
    },
    {
        'filename': 'label_x_offset13_y_offset_17.lyr'
    },
    {
        'filename': 'unique_values_grouped.lyr'
    },
    {
        'filename': 'unique_values_v3.lyr'
    },
    {
        'filename': 'unique_matched_to_symbols_highway_matched.lyr'
    },
    {
        'filename': 'unique_flip_symbols.lyr'
    },
    {
        'filename': 'unique_group_3.lyr'
    },
    {
        'filename': 'unique_group_4.lyr'
    },
    {
        'filename': 'unique_grouped_with_heading.lyr'
    },
    {
        'filename': 'picture_fill_v4.lyr'
    },
    {
        'filename': 'point_rotation_heading_arithmetic.lyr'
    },
    {
        'filename': 'point_rotation_heading_geographic.lyr'
    },
    {
        'filename': 'point_rotation_random_17_23.lyr'
    },
    {
        'filename': 'point_size_important.lyr'
    },
    {
        'filename': 'point_size_random_01_08.lyr'
    },
    {
        'filename': 'polys_transparency_value.lyr'
    },
    {
        'filename': 'labels_off.lyr'
    },
    {
        'filename': 'labels_on.lyr'
    },
    {
        'filename': 'label_text_fill.lyr'
    },
    {
        'filename': 'label_text_background.lyr'
    },
    {
        'filename': 'label_maskhalo_size19.lyr'
    },
    {
        'filename': 'label_mask_halo_symbol.lyr'
    },
    {
        'filename': 'label_below.lyr'
    },
    {
        'filename': 'label_buffer_4_7.lyr'
    },
    {
        'filename': 'label_curved.lyr'
    },
    {
        'filename': 'label_default.lyr'
    },
    {
        'filename': 'label_horizontal.lyr'
    },
    {
        'filename': 'label_offset_4_9.lyr'
    },
    {
        'filename': 'label_on_line.lyr'
    },
    {
        'filename': 'label_one_per_feature.lyr'
    },
    {
        'filename': 'label_one_per_part.lyr'
    },
    {
        'filename': 'label_orientation_line.lyr'
    },
    {
        'filename': 'label_perpendicular.lyr'
    },
    {
        'filename': 'label_place_overlapping.lyr'
    },
    {
        'filename': 'label_pos_all.lyr'
    },
    {
        'filename': 'label_weight_low.lyr'
    },
    {
        'filename': 'label_weight_med.lyr'
    },
    {
        'filename': 'label_feature_weight_none.lyr'
    },
    {
        'filename': 'label_feature_weight_low.lyr'
    },
    {
        'filename': 'label_feature_weight_med.lyr'
    },
    {
        'filename': 'label_feature_weight_high.lyr'
    },
    {
        'filename': 'label_jscript.lyr'
    },
    {
        'filename': 'label_python.lyr'
    },
    {
        'filename': 'label_vbscript.lyr'
    },
    {
        'filename': 'transparent_37.lyr'
    },
    {
        'filename': 'hyperlinks_script.lyr'
    },
    {
        'filename': 'hyperlinks_url.lyr'
    },
    {
        'filename': 'hyperlinks_using_name.lyr'
    },
    {
        'filename': 'no_scale_symbols.lyr'
    },
    {
        'filename': 'select_color_255_0_255.lyr'
    },
    {
        'filename': 'show_map_tips.lyr'
    },
    {
        'filename': 'exclusion_list.lyr'
    },
    {
        'filename': 'label_expression_python_advanced.lyr'
    },
    {
        'filename': 'point_label_angle_by_field.lyr'
    },
    {
        'filename': 'point_label_angle_by_field_perpendicular.lyr'
    },
    {
        'filename': 'symbol_levels_advanced.lyr'
    },
    {
        'filename': 'symbol_levels_points.lyr'
    },
    {
        'filename': 'unique_symbol_levels.lyr'
    },
    {
        'filename': 'unknown_coordinate_system.lyr'
    },
    {
        'filename': 'unknown_coordinate_system_v3.lyr'
    },
    {
        'filename': 'projected_v3.lyr'
    },
    {
        'filename': 'envelope_64.lyr'
    },
    {
        'filename': 'layer description.lyr'
    },
    {
        'filename': 'popup_as_url.lyr'
    },
    {
        'filename': 'popup_as_xsl.lyr'
    },
    {
        'filename': 'popup_hide_field_name.lyr'
    },
    {
        'filename': 'popup_show_coded.lyr'
    },
    {
        'filename': 'no_html_popup.lyr'
    },
    {
        'filename': 'time_data_changes_recalculate.lyr'
    },
    {
        'filename': 'time_display_cumulative.lyr'
    },
    {
        'filename': 'time_extent_1_1_0001_to_1_1_0001.lyr'
    },
    {
        'filename': 'time_extent_1_t_2.lyr'
    },
    {
        'filename': 'time_field_value_yyyy.lyr'
    },
    {
        'filename': 'time_offset_7_8_years.lyr'
    },
    {
        'filename': 'time_start_end_value_to_name.lyr'
    },
    {
        'filename': 'time_step_7_hours.lyr'
    },
    {
        'filename': 'time_step_7_years.lyr'
    },
    {
        'filename': 'time_yyyymm.lyr'
    },
    {
        'filename': 'time_yyyymmdd.lyr'
    },
    {
        'filename': 'time_yyyymmddhhmmss.lyr'
    },
    {
        'filename': 'time_zone_brisbane.lyr'
    },
    {
        'filename': 'time_zone_brisbane_daylight_savings.lyr'
    },
    {
        'filename': 'time_zone_utc_minus6.lyr'
    },
    {
        'filename': 'group_layer_3_layers.lyr'
    },
    {
        'filename': 'group_layer_credit.lyr'
    },
    {
        'filename': 'group_layer_description.lyr'
    },
    {
        'filename': 'group_layer_invisible.lyr'
    },
    {
        'filename': 'group_layer_scale_range.lyr'
    },
    {
        'filename': 'group_layer_transparency_57.lyr'
    },
    {
        'filename': 'group_use_symbol_levels.lyr'
    },
    {
        'filename': 'nested_group.lyr'
    },
    {
        'filename': 'display_exp_no_code.lyr'
    },
    {
        'filename': 'display_expression_python.lyr'
    },
    {
        'filename': 'display_expression_vbscript.lyr'
    },
    {
        'filename': 'unique_no_all_other.lyr'
    },
    {
        'filename': 'graduated_colors_0_33333_3.lyr'
    },
    {
        'filename': 'graduated_colors.lyr'
    },
    {
        'filename': 'graduated_colors_labels.lyr'
    },
    {
        'filename': 'graduated_colors_norm_percent_of_total.lyr'
    },
    {
        'filename': 'join_name_to_class_keep_all.lyr'
    },
    {
        'filename': 'graduated_show_excluded_red.lyr'
    },
    {
        'filename': 'graduated_stdev_1_4.lyr'
    },
    {
        'filename': 'relate_name_to_class.lyr'
    },
    {
        'filename': 'graduated_colors_norm_shape_length.lyr'
    },
    {
        'filename': 'label_value.lyr'
    },
    {
        'filename': 'graduated_defined_interval_1_2.lyr'
    },
    {
        'filename': 'graduated_natural_breaks.lyr'
    },
    {
        'filename': 'graduated_colors_1_2.lyr'
    },
    {
        'filename': 'join_name_to_class_keep_matching.lyr'
    },
    {
        'filename': 'layer_name.lyr'
    },
    {
        'filename': 'graduated_stdev_1.lyr'
    },
    {
        'filename': 'graduated_sampling_12345.lyr'
    },
    {
        'filename': 'graduated_geometry_interval.lyr'
    },
    {
        'filename': 'graduated_colors_norm_log.lyr'
    },
    {
        'filename': 'graduated_stdev_1_3.lyr'
    },
    {
        'filename': 'graduated_stdev_1_2.lyr'
    },
    {
        'filename': 'graduated_exclusion.lyr'
    },
    {
        'filename': 'two_joins.lyr'
    },
    {
        'filename': 'selected_width_2.7.lyr'
    },
    {
        'filename': 'label_range_502_702.lyr'
    },
    {
        'filename': 'graduated_quantile.lyr'
    },
    {
        'filename': 'graduated_colors_show_using_values.lyr'
    },
    {
        'filename': 'graduated_equal_interval.lyr'
    },
    {
        'filename': 'display_expression_vbscript_notcoded.lyr'
    },
    {
        'filename': 'show_selection_with_symbol.lyr'
    },
    {
        'filename': 'show_selection_with_color_red.lyr'
    },
    {
        'filename': 'display_expression_python_advanced.lyr'
    },
    {
        'filename': 'display_expression_jscript.lyr'
    },
    {
        'filename': 'display_expression_jscript_not_advanced.lyr'
    },
    {
        'filename': 'display_expression_jscript_advanced.lyr'
    },
    {
        'filename': 'display_dont_show_maptips_using_display_expression.lyr'
    },
    {
        'filename': 'display_expression_python_not_advanced.lyr'
    },
    {
        'filename': 'display_expression_vbscript_coded.lyr'
    },
    {
        'filename': 'display_show_maptips_using_display_expression.lyr'
    },
    {
        'filename': 'display_expression_vbscript_advanced.lyr'
    },
    {
        'filename': 'unique_value_rotation_by_attribute.lyr'
    },
    {
        'filename': 'unique_value_size_by_field.lyr'
    },
    {
        'filename': 'unique_values_rotation_arithmetic.lyr'
    },
    {
        'filename': 'unique_values_transparency_by_field.lyr'
    },
    {
        'filename': 'class_breaks_rotation_arithmetic.lyr'
    },
    {
        'filename': 'class_breaks_rotation_by_attribute.lyr'
    },
    {
        'filename': 'class_breaks_size_by_field.lyr'
    },
    {
        'filename': 'graduated_symbol_green.lyr'
    },
    {
        'filename': 'graduated_symbol_line_width_05_to_4_5.lyr'
    },
    {
        'filename': 'graduated_symbol_normalize_percent_of_total.lyr'
    },
    {
        'filename': 'graduated_symbol_size_42_to_47.lyr'
    },
    {
        'filename': 'proportional_symbol_by_area.lyr'
    },
    {
        'filename': 'proportional_symbol_by_importance.lyr'
    },
    {
        'filename': 'proportional_symbol_by_radius.lyr'
    },
    {
        'filename': 'proportional_symbol_circle.lyr'
    },
    {
        'filename': 'proportional_symbol_compensate_flannery.lyr'
    },
    {
        'filename': 'proportional_symbol_exclude.lyr'
    },
    {
        'filename': 'proportional_symbol_feet.lyr'
    },
    {
        'filename': 'proportional_symbol_feet_red_outline_1_9_width.lyr'
    },
    {
        'filename': 'proportional_symbol_lines.lyr'
    },
    {
        'filename': 'proportional_symbol_lines_decimeters.lyr'
    },
    {
        'filename': 'proportional_symbol_lines_decimeters_distance_center.lyr'
    },
    {
        'filename': 'proportional_symbol_log_normalization.lyr'
    },
    {
        'filename': 'proportional_symbol_millimeters.lyr'
    },
    {
        'filename': 'proportional_symbol_rotate_arithmetic.lyr'
    },
    {
        'filename': 'proportional_symbol_rotate_by_heading.lyr'
    },
    {
        'filename': 'proportional_symbol_square_blue.lyr'
    },
    {
        'filename': 'proportional_symbols_lines_width.lyr'
    },
    {
        'filename': 'proprtional_symbol_norm_by_attribute.lyr'
    },
    {
        'filename': 'proprtional_symbol_show_5_legend_classes.lyr'
    },
    {
        'filename': 'xy_event.lyr'
    },
    {
        'filename': 'coverage.lyr'
    },
    {
        'filename': 'edit_template_v1.lyr'
    },
    {
        'filename': 'two_joins2.lyr'
    },
    {
        'filename': 'two_relations.lyr'
    },
    {
        'filename': 'three_joins2.lyr'
    },
    {
        'filename': 'two_joins_no_relationships.lyr'
    },
    {
        'filename': 'four_joins.lyr'
    },
    {
        'filename': 'one_join.lyr'
    },
    {
        'filename': 'indexed_join.lyr'
    },
    {
        'filename': 'three_joins.lyr'
    },
    {
        'filename': 'group_layer_scale_range_deactivated.lyr'
    },
    {
        'filename': 'barchart_bar_width19_spacing_13lyr.lyr'
    },
    {
        'filename': 'pie_chart_orientation_clockwise_from_vertical.lyr'
    },
    {
        'filename': 'stacked_3d_min_thickness.lyr'
    },
    {
        'filename': 'piechart_vary_size_using_field_important.lyr'
    },
    {
        'filename': 'piechart_vary_size_appearance_compensation_flannery.lyr'
    },
    {
        'filename': 'pie_chart_show_symbol_for_excluded.lyr'
    },
    {
        'filename': 'pie_chart_display_in_3d_min_tilt_in_thinness.lyr'
    },
    {
        'filename': 'piechart_vary_size_using_sum_of_field_values_21.lyr'
    },
    {
        'filename': 'barchart_show_axis_purple_3.lyr'
    },
    {
        'filename': 'barchart_display_in_3d_min_thickness.lyr'
    },
    {
        'filename': 'barchart_no_prevent_overlap.lyr'
    },
    {
        'filename': 'stacked_bar_width_18.lyr'
    },
    {
        'filename': 'stacked_noprevent_overlap.lyr'
    },
    {
        'filename': 'stacked_normalization_percent_of_total.lyr'
    },
    {
        'filename': 'barchart_orientation_left_to_right.lyr'
    },
    {
        'filename': 'barchart_display_in_3d_max_thickness.lyr'
    },
    {
        'filename': 'barchart_normalization_staff.lyr'
    },
    {
        'filename': 'stacked_outline_purple_7.lyr'
    },
    {
        'filename': 'stacked_excluded_symbol_purple.lyr'
    },
    {
        'filename': 'barchart_no_leader_lines.lyr'
    },
    {
        'filename': 'stacked_normalization_importance.lyr'
    },
    {
        'filename': 'barchart_exclusion_filter.lyr'
    },
    {
        'filename': 'pie_chart_exclusion_filter.lyr'
    },
    {
        'filename': 'stacked_size_fixed_length.lyr'
    },
    {
        'filename': 'stacked_bar_horizontal_orientation.lyr'
    },
    {
        'filename': 'stacked_heading_green_important_blue_pilots_red.lyr'
    },
    {
        'filename': 'pie_chart_no_leader_lines.lyr'
    },
    {
        'filename': 'barchart_size_max_length_58.lyr'
    },
    {
        'filename': 'barchart_heading_green_importance_blue_pilots_red.lyr'
    },
    {
        'filename': 'stacked_exclusion_filter.lyr'
    },
    {
        'filename': 'pie_chart_display_in_3d_max_tilt_in_thinness.lyr'
    },
    {
        'filename': 'barchart_normalization_percent_of_total.lyr'
    },
    {
        'filename': 'stacked_no_leader.lyr'
    },
    {
        'filename': 'barchart_excluded_data_purple.lyr'
    },
    {
        'filename': 'stacked_3d_max_thickness.lyr'
    },
    {
        'filename': 'pie_chart_display_in_3d_max_tilt_max_thinness.lyr'
    },
    {
        'filename': 'piechart_vary_size_by_field_normalized_log.lyr'
    },
    {
        'filename': 'piechart_vary_size_normalize_heading.lyr'
    },
    {
        'filename': 'pie_chart_orientation_anticlockwise_from_horizontal.lyr'
    },
    {
        'filename': 'pie_chart_purple_outline_size_3.lyr'
    },
    {
        'filename': 'stacked_max_length_48.lyr'
    },
    {
        'filename': 'pie_chart_heading_green_pilots_red_staff_blue.lyr'
    },
    {
        'filename': 'pie_chart_no_prevent_overlap.lyr'
    },
    {
        'filename': 'geopackage_source.lyr'
    },
    {
        'filename': 'labels_multi_class.lyr'
    },
    {
        'filename': 'label_classes_from_symbology.lyr'
    },
    {
        'filename': 'labels_multi_class_disabled.lyr'
    },
    {
        'filename': 'mapserver_red_background.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_no_transparent_color.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_png_32.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_jpg.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_png.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_png24.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_format_png32.lyr',
        'skip': True
    },
    {
        'filename': 'mapserver_background_color_transparent.lyr',
        'skip': True
    },
    {
        'filename': 'lines_not_selectable.lyr',
    },
    {
        'filename': 'lines_symbol_levels_no_join_no_merge.lyr'
    },
    {
        'filename': 'lines_no_symbol_levels.lyr'
    },
    {
        'filename': 'lines_symbol_levels_arterial_join_highway_no_join.lyr'
    },
    {
        'filename': 'group_symbol_levels.lyr'
    },
    {
        'filename': 'lines_symbol_levels_arterial_join_and_merge.lyr'
    },
    {
        'filename': 'lines_draw_using_symbol_levels_join.lyr'
    },
    {
        'filename': 'lines_draw_using_symbol_levels_no_join.lyr'
    },
    {
        'filename': 'layer_move_field_class_to_end.lyr'
    },
    {
        'filename': 'layer_cached_true.lyr'
    },
    {
        'filename': 'layer_aoi_1_2_3_4.lyr'
    },
    {
        'filename': 'layer_show_tips_false.lyr'
    },
    {
        'filename': 'hyperlink_macro_name.lyr'
    },
    {
        'filename': 'layer_brightness_100.lyr'
    },
    {
        'filename': 'popup_html_no_download_attachment.lyr'
    },
    {
        'filename': 'layer_definition_search_order_spatial.lyr'
    },
    {
        'filename': 'html_popup_enabled.lyr'
    },
    {
        'filename': 'display_field.lyr'
    },
    {
        'filename': 'layer_definition_search_order_attribute.lyr'
    },
    {
        'filename': 'html_popup_disabled.lyr'
    },
    {
        'filename': 'popup_html_redirect_field.lyr'
    },
    {
        'filename': 'popup_html_download_attachment.lyr'
    },
    {
        'filename': 'layer_show_tips_true.lyr'
    },
    {
        'filename': 'layer_cached_false.lyr'
    },
    {
        'filename': 'brightness_50.lyr'
    },
    {
        'filename': 'time_dimension_name.lyr'
    },
    {
        'filename': 'time_dimension_format.lyr'
    },
    {
        'filename': 'track_id_field_name.lyr'
    },
    {
        'filename': 'time_value_format.lyr'
    },
    {
        'filename': 'representations.lyr'
    },
    {
        'filename': 'representation_symbology_point_legend_all.lyr'
    },
    {
        'filename': 'representation_symbology_point.lyr'
    },
    {
        'filename': 'representation_symbology_point_mm.lyr'
    },
    {
        'filename': 'representation_symbology_point_legend_none.lyr'
    },
    {
        'filename': 'raster_rgb_stats_from_each_dataset.lyr'
    },
    {
        'filename': 'raster_classified_nodata_color_red.lyr'
    },
    {
        'filename': 'raster_unique_grouped.lyr'
    },
    {
        'filename': 'dot_density_maintain_density_by_dot_value.lyr'
    },
    {
        'filename': 'basemap_two_layers.lyr'
    },
    {
        'filename': 'raster_unique_values_all_other_checked.lyr'
    },
    {
        'filename': 'raster_classified_use_hillshade_z13.lyr'
    },
    {
        'filename': 'raster_bilinear.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpen_type_bovey.lyr'
    },
    {
        'filename': 'basemap_scalerange.lyr'
    },
    {
        'filename': 'raster_show_resolution_in_toc.lyr'
    },
    {
        'filename': 'raster_stretch_histogram_equalize.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpen_weights_123_ir4lyr.lyr'
    },
    {
        'filename': 'raster_discrete_color_255.lyr'
    },
    {
        'filename': 'raster_time_step_99hours.lyr'
    },
    {
        'filename': 'raster_extent_current_setting.lyr'
    },
    {
        'filename': 'raster_display_background_value_77.lyr'
    },
    {
        'filename': 'raster_classified_show_class_breaks_using_cell_values.lyr'
    },
    {
        'filename': '10 x 10 Degree Graticule.lyr'
    },
    {
        'filename': 'raster_stretched_stats_from_each_dataset.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpen_type_ihs.lyr'
    },
    {
        'filename': 'raster_stretched_band_5.lyr'
    },
    {
        'filename': 'raster_stretched.lyr'
    },
    {
        'filename': 'raster_time_offset_39minutes.lyr'
    },
    {
        'filename': 'dot_density_exclusion_filter.lyr'
    },
    {
        'filename': 'raster_stretched_type_none.lyr'
    },
    {
        'filename': 'dot_density_maintain_density_by_dot_size.lyr'
    },
    {
        'filename': 'raster_rgb_bands123.lyr'
    },
    {
        'filename': 'raster_stretch_from_custom_settings.lyr'
    },
    {
        'filename': 'raster_rgb_stretch_minmax.lyr'
    },
    {
        'filename': 'raster_rgb_stretch_params_rgb_200_contrast_50.lyr'
    },
    {
        'filename': 'raster_rgb_stretch_invert.lyr'
    },
    {
        'filename': 'raster_layer_zoom_range.lyr'
    },
    {
        'filename': 'raster_classified_labels.lyr'
    },
    {
        'filename': 'raster_rgb_nodata_color_blue.lyr'
    },
    {
        'filename': 'raster_rgb_stretch_stdev_4_5.lyr'
    },
    {
        'filename': 'raster_rgb_alpha_checked.lyr'
    },
    {
        'filename': 'raster_stretched_labels.lyr',
    },
    {
        'filename': 'raster_rgb_stretch_esri.lyr'
    },
    {
        'filename': 'raster_rgb_bg_119_139_159.lyr'
    },
    {
        'filename': 'layer_v23.lyr'
    },
    {
        'filename': 'raster_rgb_background_color_red.lyr'
    },
    {
        'filename': 'dot_density_2.lyr'
    },
    {
        'filename': 'basemap_invisible.lyr'
    },
    {
        'filename': 'basemap_attributes.lyr'
    },
    {
        'filename': 'basemap_deactivated_scalerange].lyr'
    },
    {
        'filename': 'raster_classified.lyr'
    },
    {
        'filename': 'raster_stretch_standard_deviations_2_5.lyr'
    },
    {
        'filename': 'raster_rgb_gamma_stretch_2_3_4.lyr'
    },
    {
        'filename': 'dot_density_use_masking_place_only_in.lyr'
    },
    {
        'filename': 'raster_rgb_display_background_value.lyr'
    },
    {
        'filename': 'dot_density_red_blue.lyr'
    },
    {
        'filename': 'raster_stretch_min_max.lyr'
    },
    {
        'filename': 'dot_density_dot_size_5_density_7000.lyr'
    },
    {
        'filename': 'raster_classified_3_breaks.lyr'
    },
    {
        'filename': 'raster_stretched_ramp.lyr'
    },
    {
        'filename': 'raster_stretched_stats_custom.lyr'
    },
    {
        'filename': 'raster_layer.lyr'
    },
    {
        'filename': 'raster_stretch_apply_gamma_1_9.lyr'
    },
    {
        'filename': 'raster_custom_extent_4321.lyr'
    },
    {
        'filename': 'raster_stretched_labels_interval_37.lyr'
    },
    {
        'filename': 'raster_rgb_red_checked.lyr'
    },
    {
        'filename': 'raster_unique_labels.lyr'
    },
    {
        'filename': 'raster_enable_time.lyr'
    },
    {
        'filename': 'raster_rgb_alpha_b4.lyr'
    },
    {
        'filename': 'dot_density_fixed_placement_seed4815lyr.lyr'
    },
    {
        'filename': 'dot_density_mask_exclude_in.lyr'
    },
    {
        'filename': 'raster_layer_attributes.lyr'
    },
    {
        'filename': 'raster_rgb_alpha_band7.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpen_type_mean.lyr'
    },
    {
        'filename': 'raster_time_step_99_decades.lyr'
    },
    {
        'filename': 'raster_rgb_no_bands_checked.lyr'
    },
    {
        'filename': 'raster_stretched_display_background_color_red.lyr'
    },
    {
        'filename': 'raster_rgb_blue_checked.lyr'
    },
    {
        'filename': 'layer_v25.lyr'
    },
    {
        'filename': 'raster_layer_unchecked.lyr'
    },
    {
        'filename': 'raster_display_medium.lyr'
    },
    {
        'filename': 'raster_discrete_color_35.lyr'
    },
    {
        'filename': 'raster_rgb_green_checked.lyr'
    },
    {
        'filename': 'raster_display_coarse.lyr'
    },
    {
        'filename': 'raster_unique_values_all_other_unchecked.lyr'
    },
    {
        'filename': 'colormap255_nodata_red.lyr'
    },
    {
        'filename': 'raster_stretched_none_invert.lyr'
    },
    {
        'filename': 'raster_primary_display_count.lyr'
    },
    {
        'filename': 'raster_layer_no_zoom_range.lyr'
    },
    {
        'filename': 'raster_cubic.lyr'
    },
    {
        'filename': 'raster_stretch_sigmoid_strength_6.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpen_using_dem.lyr'
    },
    {
        'filename': 'dot_density_legend_for_excluded.lyr'
    },
    {
        'filename': 'raster_rgb_red_blue_unchecked.lyr'
    },
    {
        'filename': 'raster_stretched_use_hillshade_z_19.lyr'
    },
    {
        'filename': 'raster_stretched_band8.lyr'
    },
    {
        'filename': 'raster_resample_majority.lyr'
    },
    {
        'filename': 'raster_extent_current_display.lyr'
    },
    {
        'filename': 'unique_lookup.lyr'
    },
    {
        'filename': 'raster_stretched_stats_from_display_extent.lyr'
    },
    {
        'filename': 'raster_extent_full.lyr'
    },
    {
        'filename': 'colormap_labels.lyr'
    },
    {
        'filename': 'dot_density_ramp.lyr'
    },
    {
        'filename': 'raster_discrete_color_nodata_red.lyr'
    },
    {
        'filename': 'raster_stretched_type_histogram_spec.lyr'
    },
    {
        'filename': 'raster_two_relates.lyr'
    },
    {
        'filename': 'raster_join_keep_matching.lyr'
    },
    {
        'filename': 'raster_primary_display_value.lyr'
    },
    {
        'filename': 'raster_two_joins.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpen_no_4th_band_as_infrared.lyr'
    },
    {
        'filename': 'raster_unique_complex_legend.lyr'
    },
    {
        'filename': 'raster_show_maptips.lyr'
    },
    {
        'filename': 'raster_classified_5_break.lyr'
    },
    {
        'filename': 'dot_density_no_maintain_density.lyr'
    },
    {
        'filename': 'raster_unique_band_8.lyr'
    },
    {
        'filename': 'raster_stretched_9_interval_labels.lyr'
    },
    {
        'filename': 'raster_stretched_type_custom.lyr'
    },
    {
        'filename': 'raster_constrast_33_brightness_34_transparency_35.lyr'
    },
    {
        'filename': 'raster_discrete_band_8.lyr'
    },
    {
        'filename': 'raster_rgb_stats_from_current_display.lyr'
    },
    {
        'filename': 'raster_rgb_bands876.lyr'
    },
    {
        'filename': 'colormap_nodata_red.lyr'
    },
    {
        'filename': 'dot_density.lyr'
    },
    {
        'filename': 'dot_density_green_background_red_outline.lyr'
    },
    {
        'filename': 'raster_relate.lyr'
    },
    {
        'filename': 'raster_join_keep_all.lyr'
    },
    {
        'filename': 'raster_allow_interactive_display.lyr'
    },
    {
        'filename': 'raster_rgb_pansharpening_enabled.lyr'
    },
    {
        'filename': 'raster_rgb_stats_from_custom.lyr'
    },
    {
        'filename': 'raster_stretched_percent_clip_34_96.lyr'
    },
    {
        'filename': 'raster_stretched_display_nodata_color_green.lyr'
    },
    {
        'filename': 'colormap_255.lyr'
    },
    {
        'filename': 'colormap_20.lyr'
    },
    {
        'filename': 'raster_pansharpen_type_esri.lyr'
    },
    {
        'filename': 'raster_time_offset_39years.lyr'
    },
    {
        'filename': 'raster_resample_nearest_neighbour.lyr'
    },
    {
        'filename': 'raster_rgb_sigmoid_strength_6.lyr'
    },
    {
        'filename': 'raster_rgb_percent_clip_17_83.lyr'
    },
    {
        'filename': 'raster_rgb_stretch_none.lyr'
    },
]

initialize_registry()


class TestLyrParser(unittest.TestCase):
    """
    Test LYR parsing
    """

    UPDATE = True

    # pylint: disable=too-many-locals
    def test_lyr_parsing(self):
        """
        Checks all lyr parsing against expectations
        """
        blobs = []
        path = os.path.join(os.path.dirname(__file__), 'lyr')
        for fn in os.listdir(path):
            file = os.path.join(path, fn)
            if os.path.isfile(file):
                blobs.append(fn)
        some_missing = False
        for b in blobs:
            if not [e for e in expected if e['filename'] == b]:
                print("""{
                   'filename': '""" + b + """',
                   'skip': True
               },""")
            some_missing = some_missing or not bool([e for e in expected if e['filename'] == b])
        assert not some_missing

        for e in expected:
            if 'skip' in e:
                continue

            offset = e.get('offset', 0)
            file = os.path.join(os.path.dirname(__file__), 'lyr', e['filename'])
            base, _ = os.path.splitext(e['filename'])
            expected_file = os.path.join(os.path.dirname(__file__), 'lyr', 'expected', base + str(hex(offset)) + '.txt')
            with open(file, 'rb') as f:
                print('{}:{}'.format(e['filename'], hex(offset)))

                doc = LayerFile(f, debug=False, offset=-1, tolerant=False, check_length=True)
                d = doc.to_dict()

                if self.UPDATE:
                    with open(expected_file, 'w', encoding='UTF-8') as o:
                        pprint.pprint(d, o)
                else:
                    with open(expected_file, 'r', encoding='UTF-8') as o:
                        expected_res = ast.literal_eval(o.read())
                    self.assertEqual(expected_res, d)

    # pylint: enable=too-many-locals


if __name__ == '__main__':
    unittest.main()
