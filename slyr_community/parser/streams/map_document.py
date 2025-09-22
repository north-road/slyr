import os
from typing import Optional

from ..stream import Stream
from ..exceptions import EmptyDocumentException, DocumentTypeException


class MapDocument:
    def __init__(
        self,
        io_stream,
        debug: bool = False,
        offset: int = 0,
        tolerant=True,
        check_length=False,
        read_layouts=False,
        metadata_only=False,
    ):
        self.version = ""
        self.major_version = 0
        self.title = ""
        self.author = ""
        self.description = ""
        self.summary = ""
        self.tags = ""
        self.hyperlink_base = ""
        self.credits = ""
        self.original_path = ""
        self.last_saved = None
        self.last_printed = None
        self.last_exported = None
        self.frames = []
        self.default_toc_symbol_width = 12
        self.default_toc_symbol_height = 12
        self.default_fill = None
        self.default_line = None
        self.default_marker = None
        self.default_area_patch = None
        self.default_line_patch = None
        self.default_text_symbol = None
        self.default_callout_symbol = None
        self.template_paths = []
        self.toc_view_mode = "Display"
        self.selection_environment = None
        self.style_gallery = None
        self.page_layout = None
        self.active_frame = None
        self.use_relative_sources = False
        self.default_database = None
        self.table_properties = None
        self.layout_read_error: Optional[str] = None

        if io_stream.read(4) != b"\xd0\xcf\x11\xe0":
            raise DocumentTypeException()

        io_stream.seek(io_stream.tell() - 4)

        stream = Stream(
            io_stream,
            debug=debug,
            offset=offset,
            force_layer=True,
            extract_doc_structure=True,
            tolerant=tolerant,
            parse_doc_structure_only=True,
        )

        if not stream.directories:
            raise EmptyDocumentException()

        version_stream = stream.extract_file_from_stream("Version")
        document_version_info = stream.extract_file_from_stream(
            "Mx Document Version Info"
        )
        metadata_stream = stream.extract_file_from_stream("Metadata")
        templates_stream = stream.extract_file_from_stream("Templates")
        style_gallery_stream = stream.extract_file_from_stream("StyleGallery")
        drawing_defaults_stream = stream.extract_file_from_stream("DrawingDefaults")
        document_stream = stream.extract_file_from_stream("Mx Document")
        maps_stream = stream.extract_file_from_stream("Maps")
        page_layout_stream = stream.extract_file_from_stream("PageLayout")

        view_stream = None
        table_properties_stream = None
        document_database_stream = None

        if version_stream:
            stream.io_stream = version_stream
            self.read_version(stream)
            if check_length:
                pos = version_stream.tell()
                version_stream.seek(0, os.SEEK_END)
                assert pos == version_stream.tell(), (
                    "Did not read to end of Version stream. Read to {} of {}".format(
                        hex(pos), hex(version_stream.tell())
                    )
                )

        if document_version_info:
            stream.io_stream = document_version_info
            self.read_document_version(stream)
            stream.objects[-1] = {}
            if check_length:
                pos = version_stream.tell()
                version_stream.seek(0, os.SEEK_END)
                assert pos == version_stream.tell(), (
                    "Did not read to end of Mx Document Version Info stream. Read to {} of {}".format(
                        hex(pos), hex(version_stream.tell())
                    )
                )

        if metadata_stream:
            stream.io_stream = metadata_stream
            self.read_metadata(stream)
            if check_length:
                pos = metadata_stream.tell()
                metadata_stream.seek(0, os.SEEK_END)
                assert pos == metadata_stream.tell(), (
                    "Did not read to end of Metadata stream. Read to {} of {}".format(
                        hex(pos), hex(metadata_stream.tell())
                    )
                )

        if templates_stream and not metadata_only:
            stream.io_stream = templates_stream
            self.read_templates(stream, bool(drawing_defaults_stream))
            if check_length:
                pos = templates_stream.tell()
                templates_stream.seek(0, os.SEEK_END)
                assert pos == templates_stream.tell(), (
                    "Did not read to end of Templates stream. Read to {} of {}".format(
                        hex(pos), hex(templates_stream.tell())
                    )
                )

        if style_gallery_stream and not metadata_only:
            stream.io_stream = style_gallery_stream
            self.read_style_gallery(stream)
            if check_length:
                pos = style_gallery_stream.tell()
                style_gallery_stream.seek(0, os.SEEK_END)
                assert pos == style_gallery_stream.tell(), (
                    "Did not read to end of StyleGallery stream. Read to {} of {}".format(
                        hex(pos), hex(style_gallery_stream.tell())
                    )
                )

        if drawing_defaults_stream and not metadata_only:
            stream.io_stream = drawing_defaults_stream
            self.read_drawing_defaults(stream)
            if check_length:
                pos = drawing_defaults_stream.tell()
                drawing_defaults_stream.seek(0, os.SEEK_END)
                assert pos == drawing_defaults_stream.tell(), (
                    "Did not read to end of DrawingDefaults stream. Read to {} of {}".format(
                        hex(pos), hex(drawing_defaults_stream.tell())
                    )
                )

        if document_stream and not metadata_only:
            stream.objects[-1] = {}
            stream.io_stream = document_stream
            stream.read_int("unknown", expected=1)
            stream.read_int("unknown", expected=1)
            stream.read_int("unknown", expected=1)
        else:
            stream.io_stream = maps_stream

        if stream.io_stream and not metadata_only:
            self.read_maps(stream, bool(document_stream))
            if not document_stream and check_length:
                pos = maps_stream.tell()
                maps_stream.seek(0, os.SEEK_END)
                assert pos == maps_stream.tell(), (
                    "Did not read to end of Maps stream. Read to {} of {}".format(
                        hex(pos), hex(maps_stream.tell())
                    )
                )
            elif document_stream:
                if not tolerant or read_layouts:
                    try:
                        self.read_layout(stream)
                    except Exception as e:
                        self.layout_read_error = str(e)

        if page_layout_stream and not document_stream and not metadata_only:
            stream.io_stream = page_layout_stream
            if not tolerant or read_layouts:
                try:
                    self.read_layout(stream)
                except Exception as e:
                    self.layout_read_error = str(e)
                if False and check_length:
                    pos = page_layout_stream.tell()
                    page_layout_stream.seek(0, os.SEEK_END)
                    assert pos == page_layout_stream.tell(), (
                        "Did not read to end of PageLayout stream. Read to {} of {}".format(
                            hex(pos), hex(page_layout_stream.tell())
                        )
                    )

        if view_stream and not metadata_only:
            stream.io_stream = view_stream
            if not tolerant:
                self.read_view(stream)
                if check_length:
                    pos = view_stream.tell()
                    view_stream.seek(0, os.SEEK_END)
                    assert pos == view_stream.tell(), (
                        "Did not read to end of View stream. Read to {} of {}".format(
                            hex(pos), hex(view_stream.tell())
                        )
                    )

        if table_properties_stream and not metadata_only:
            if not tolerant:
                stream.io_stream = table_properties_stream
                self.table_properties = stream.read_object("table properties")
                if check_length:
                    pos = table_properties_stream.tell()
                    table_properties_stream.seek(0, os.SEEK_END)
                    assert pos == table_properties_stream.tell(), (
                        "Did not read to end of TableProperties stream. Read to {} of {}".format(
                            hex(pos), hex(table_properties_stream.tell())
                        )
                    )

        if document_database_stream and not tolerant and not metadata_only:
            stream.io_stream = document_database_stream
            self.default_database = stream.read_object("default database")
            if check_length:
                pos = document_database_stream.tell()
                document_database_stream.seek(0, os.SEEK_END)
                assert pos == document_database_stream.tell(), (
                    "Did not read to end of DocumentDatabase stream. Read to {} of {}".format(
                        hex(pos), hex(document_database_stream.tell())
                    )
                )

        # search for holes in references
        if not tolerant:
            for i in range(len(stream.objects[-1])):
                if i not in stream.objects[-1]:
                    print("WARNING: missing ref {}".format(i))

    def read_version(self, stream):
        self.version = stream.read_string("version")
        self.major_version = stream.read_ushort("major version")  # 16 =9.3, 23=10.6?
        if self.major_version > 10:
            stream.read_int(
                "unknown"
            )  # maybe minor/patch revision? e.g. 58, 64, 67, 82, 131, 132, 138, 143, 185

    def read_document_version(self, stream):
        stream.read_int("unknown", expected=1)
        properties = stream.read_object("version properties")
        self.version = properties.properties["Build Number"]

    def read_metadata(self, stream):
        try:
            major_version_from_string = (
                int(self.version.split(".")[0]) if self.version else None
            )
        except ValueError:
            major_version_from_string = None

        if (
            (not major_version_from_string or major_version_from_string < 10)
            and self.major_version
            and self.major_version <= 16
        ):
            self.title = stream.read_string("title")
            self.author = stream.read_string("author")
            stream.read_string("unknown", expected="")
            stream.read_string("unknown", expected="")
            stream.read_string("unknown", expected="")
            stream.read_string("unknown", expected="")
            stream.read_int("unknown", expected=0)
            stream.read_string("unknown", expected="")
            stream.read_string("unknown", expected="")
        else:
            version = stream.read_ushort("version", expected=(3, 4))
            self.title = stream.read_string("title")
            self.author = stream.read_string("author")
            self.description = stream.read_string("description")
            self.summary = stream.read_string("summary")
            stream.read_string("unknown", expected="")
            self.tags = stream.read_string("tags")
            stream.read_int("unknown", expected=(0, 1))
            self.hyperlink_base = stream.read_string("hyperlink base")
            stream.read_string("unknown", expected="")
            self.credits = stream.read_string("credits")
            self.original_path = stream.read_string("original path?")

            self.last_saved = stream.read_variant(Stream.VBDATE, "last saved")
            self.last_printed = stream.read_variant(Stream.VBDATE, "last printed")
            self.last_exported = stream.read_variant(Stream.VBDATE, "last exported")

            self.use_relative_sources = stream.read_int("use relative sources") != 0
            if version > 3:
                stream.read_string("unknown", expected="")

    def read_templates(self, stream, has_drawing_defaults):
        count = stream.read_int("template count")
        for i in range(count):
            self.template_paths.append(
                stream.read_string("template path {}".format(i + 1))
            )
            stream.read_int("unknown", expected=1)
        stream.read_int("unknown", expected=(3, 5))

        if self.major_version > 9:
            if not has_drawing_defaults:
                self.default_fill = stream.read_object("default fill")
                self.default_line = stream.read_object("default line")
                self.default_marker = stream.read_object("default marker")
                self.default_text_symbol = stream.read_object("default text symbol")
                self.default_callout_symbol = stream.read_object(
                    "default callout symbol"
                )
                self.default_area_patch = stream.read_object("default area patch")
                self.default_line_patch = stream.read_object("default line patch")

                self.default_toc_symbol_width = stream.read_double(
                    "default toc symbol width"
                )
                self.default_toc_symbol_height = stream.read_double(
                    "default toc symbol height"
                )

            stream.read_string("default font?")
            stream.read_double(
                "font size??"
            )  # , expected=(0, 11, 2061745644852025.5, 4.3257934243725296e-268, 1.213859894000235e-304))
            string_count = stream.read_int("string count")
            for i in range(string_count):
                stream.read_string("unknown string {}".format(i + 1))
                stream.read_ushort("unknown", expected=65535)

            self.toc_view_mode = stream.read_string(
                "toc current view mode",
                expected=("Display", "Source", "Selection", "Visible"),
            )
            self.selection_environment = stream.read_object("selection environment")
            if self.major_version < 16:
                stream.read_object("unknown latlong format")
                stream.read_object("unknown numeric format")
        elif self.major_version > 5:
            self.default_fill = stream.read_object("default fill")
            self.default_line = stream.read_object("default line")
            self.default_marker = stream.read_object("default marker")
            self.default_text_symbol = stream.read_object("default text symbol")
            self.default_callout_symbol = stream.read_object("default callout symbol")
            self.default_area_patch = stream.read_object("default area patch")
            self.default_line_patch = stream.read_object("default line patch")
        else:
            stream.read_object("unknown font")

    def read_style_gallery(self, stream):
        self.style_gallery = stream.read_object("style gallery")

    def read_drawing_defaults(self, stream):
        self.default_fill = stream.read_object("default fill")
        self.default_line = stream.read_object("default line")
        self.default_marker = stream.read_object("default marker")
        self.default_text_symbol = stream.read_object("default text symbol")
        self.default_callout_symbol = stream.read_object("default callout symbol")
        self.default_area_patch = stream.read_object("default area patch")
        self.default_line_patch = stream.read_object("default line patch")
        self.default_toc_symbol_width = stream.read_double("default toc symbol width")
        self.default_toc_symbol_height = stream.read_double("default toc symbol height")

    def read_maps(self, stream, is_document_stream):
        data_frame_count = stream.read_int("data frame count")
        if data_frame_count == 0:
            raise EmptyDocumentException()

        for i in range(data_frame_count):
            self.frames.append(stream.read_object("data frame {}".format(i + 1)))

        if not is_document_stream:
            # maybe related to relative sources??
            stream.read_int("unknown", expected=(0, 1))

    def read_layout(self, stream):
        self.page_layout = stream.read_object("page layout")

    def read_view(self, stream):
        version = stream.read_ushort("version", expected=(1, 2))
        self.active_frame = stream.read_object("window")
        if version > 1:
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_object("unknown format")
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_int("unknown", expected=0)
            stream.read_ushort("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "version": self.version,
            "major_version": self.major_version,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "summary": self.summary,
            "tags": self.tags,
            "hyperlink_base": self.hyperlink_base,
            "credits": self.credits,
            "original_path": self.original_path,
            "last_saved": self.last_saved,
            "last_printed": self.last_printed,
            "last_exported": self.last_exported,
            "frames": [f.to_dict() for f in self.frames],
            "default_toc_symbol_width": self.default_toc_symbol_width,
            "default_toc_symbol_height": self.default_toc_symbol_height,
            "default_fill": self.default_fill.to_dict() if self.default_fill else None,
            "default_line": self.default_line.to_dict() if self.default_line else None,
            "default_marker": self.default_marker.to_dict()
            if self.default_marker
            else None,
            "default_area_patch": self.default_area_patch.to_dict()
            if self.default_area_patch
            else None,
            "default_line_patch": self.default_line_patch.to_dict()
            if self.default_line_patch
            else None,
            "template_paths": self.template_paths,
            "toc_view_mode": self.toc_view_mode,
            "selection_environment": self.selection_environment.to_dict()
            if self.selection_environment
            else None,
            "style_gallery": self.style_gallery.to_dict()
            if self.style_gallery
            else None,
            "page_layout": self.page_layout.to_dict() if self.page_layout else None,
            "table_properties": self.table_properties.to_dict()
            if self.table_properties
            else None,
            "default_database": self.default_database.to_dict()
            if self.default_database
            else None,
            "active_frame": self.active_frame,
            "use_relative_sources": self.use_relative_sources,
            "default_text_symbol": self.default_text_symbol.to_dict()
            if self.default_text_symbol
            else None,
            "default_callout_symbol": self.default_callout_symbol.to_dict()
            if self.default_callout_symbol
            else None,
        }
