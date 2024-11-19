import re
from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Pango
from .noDirSelectedGreeting import noDirSelectedGreeting
from .songCard import songCard
from .syncLine import syncLine
from .fileDetails import fileDetails
from .parsers import timing_parser, arg_timing_parser
from . import main
from . import shared

@Gtk.Template(resource_path='/io/github/dzheremi2/lrcmake_gtk/gtk/window.ui')
class LrcmakeWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'LrcmakeWindow'

    music_lib = Gtk.Template.Child()
    nav_view = Gtk.Template.Child()
    syncing = Gtk.Template.Child()
    sync_page_cover = Gtk.Template.Child()
    sync_page_title = Gtk.Template.Child()
    sync_page_artist = Gtk.Template.Child()
    lyrics_lines_box = Gtk.Template.Child()
    add_line_button = Gtk.Template.Child()
    controls = Gtk.Template.Child()
    toggle_repeat = Gtk.Template.Child()
    sync_line_button = Gtk.Template.Child()
    playing_info_button = Gtk.Template.Child()
    rew100_button = Gtk.Template.Child()
    forw100_button = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    export_lyrics = Gtk.Template.Child()

    title = None
    artist = None
    filename = None
    filepath = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.syncing.connect('hiding', self.reset_sync_editor)
        self.add_line_button.connect('clicked', self.append_line_end)
        self.syncing.connect('showing', self.on_sync_editor_open)
        self.toggle_repeat.connect('toggled', self.do_toggle_repeat)
        self.sync_line_button.connect('clicked', self.do_sync)
        self.playing_info_button.connect('clicked', self.show_details)
        self.rew100_button.connect('clicked', self.do_100ms_rew)
        self.forw100_button.connect('clicked', self.do_100ms_forw)

        if self.music_lib.get_child_at_index(0) == None:
            self.music_lib.set_property('halign', 'center')
            self.music_lib.set_property('valign', 'center')
            self.music_lib.set_property('homogeneous', False)
            self.music_lib.append(noDirSelectedGreeting())

    def reset_sync_editor(self, *args):
        self.lyrics_lines_box.remove_all()
        shared.shared.selected_row = None
        self.controls.get_media_stream().stream_ended()
        self.toggle_repeat.set_active(False)
        main.app.win.remove_action("add_line_below_selected")
        main.app.win.remove_action("remove_selected_line")
        main.app.win.remove_action("add_line_over_selected")
        main.app.win.remove_action("do_sync")
        main.app.win.remove_action("append_line_end")

    def append_line_end(self, *args):
        self.lyrics_lines_box.append(syncLine())

    def remove_selected_line(self, *args):
        self.lyrics_lines_box.remove(shared.shared.selected_row)

    def prepend_line(self, *args):
        if shared.shared.selected_row in self.lyrics_lines_box:
            childs = []
            for child in self.lyrics_lines_box:
                childs.append(child)
            index = childs.index(shared.shared.selected_row)
            if index > 0:
                self.lyrics_lines_box.insert(syncLine(), index)
            elif index == 0:
                self.lyrics_lines_box.prepend(syncLine())

    def append_line(self, *args):
        if shared.shared.selected_row in self.lyrics_lines_box:
            childs = []
            for child in self.lyrics_lines_box:
                childs.append(child)
            index = childs.index(shared.shared.selected_row)
            self.lyrics_lines_box.insert(syncLine(), index+1)

    def on_sync_editor_open(self, *args):
        self.lyrics_lines_box.append(syncLine())
        main.app.create_action("add_line_below_selected", self.append_line, ['<primary>a'])
        main.app.create_action("remove_selected_line", self.remove_selected_line, ['<primary>d'])
        main.app.create_action("add_line_over_selected", self.prepend_line, ['<primary><shift>a'])
        main.app.create_action("append_line_end", self.append_line_end, ['<Alt>a'])
        main.app.create_action("do_sync", self.do_sync, ['<Alt>Return'])
        main.app.create_action("do_100ms_rew", self.do_100ms_rew, ['<Alt>minus'])
        main.app.create_action("do_100ms_forw", self.do_100ms_forw, ['<Alt>equal'])
        self.controls.get_media_stream().connect("notify::timestamp", self.on_timestamp_changed)

    def do_100ms_rew(self, *args):
        pattern = r'\[([^\[\]]+)\]'
        if timing_parser() >= 100:
            timestamp = timing_parser() - 100
            new_timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}]"
            replacement = fr'{new_timestamp}'
            shared.shared.selected_row.set_text(re.sub(pattern, replacement, shared.shared.selected_row.get_text()))
            self.controls.get_media_stream().seek(timestamp * 1000)
        else:
            replacement = fr'[00:00.000]'
            shared.shared.selected_row.set_text(re.sub(pattern, replacement, shared.shared.selected_row.get_text()))
            self.controls.get_media_stream().seek(0)

    def do_100ms_forw(self, *args):
        pattern = r'\[([^\[\]]+)\]'
        timestamp = timing_parser() + 100
        new_timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}]"
        replacement = fr'{new_timestamp}'
        shared.shared.selected_row.set_text(re.sub(pattern, replacement, shared.shared.selected_row.get_text()))
        self.controls.get_media_stream().seek(timestamp * 1000)


    def do_sync(self, *args):
        pattern = r'\[([^\[\]]+)\] '
        timestamp = self.controls.get_media_stream().get_timestamp() // 1000
        timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}] "
        if shared.shared.selected_row in self.lyrics_lines_box:
            childs = []
            for child in self.lyrics_lines_box:
                childs.append(child)
            index = childs.index(shared.shared.selected_row)
        else:
            pass
        if re.search(pattern, shared.shared.selected_row.get_text()) == None:
            shared.shared.selected_row.set_text(timestamp + shared.shared.selected_row.get_text())
        else:
            replacement = fr'{timestamp}'
            shared.shared.selected_row.set_text(re.sub(pattern, replacement, shared.shared.selected_row.get_text()))
        if self.lyrics_lines_box.get_row_at_index(index+1) != None:
            for_focus_line = self.lyrics_lines_box.get_row_at_index(index+1)
            for_focus_line.grab_focus()
        else:
            pass

    def do_toggle_repeat(self, *args):
        if self.toggle_repeat.get_active():
            self.controls.get_media_stream().set_loop(True)
        else:
            self.controls.get_media_stream().set_loop(False)

    def show_details(self, *args):
        dialog = fileDetails(title = self.title, artist = self.artist, filename = self.filename)
        dialog.properties.append(Adw.ActionRow(title = _("Loaded from Filepath"), subtitle = self.filepath, css_classes = ['property']))
        dialog.present(main.app.win)

    def on_timestamp_changed(self, media_stream, _):
        attributes = Pango.AttrList().from_string("0 -1 weight ultrabold")
        try:
            childs = []
            timestamps = []
            for child in self.lyrics_lines_box:
                childs.append(child)
                timestamps.append(arg_timing_parser(child.get_text()))
                child.set_attributes(None)
            timestamp = media_stream.get_timestamp() // 1000
            for i in range(len(timestamps) - 1):
                if timestamp >= timestamps[i] and timestamp < timestamps[i+1]:
                    childs[i].set_attributes(attributes)
                    break
                elif timestamp >= timestamps[-1]:
                    childs[-1].set_attributes(attributes)
        except (TypeError, AttributeError):
            pass