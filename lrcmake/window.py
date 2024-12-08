import re
from gi.repository import Adw, Gtk, Pango  # type: ignore
from lrcmake.components.syncLine import syncLine
from lrcmake.components.fileDetails import fileDetails
from lrcmake.methods.parsers import timing_parser, arg_timing_parser, sorting
from lrcmake.methods.exportData import arg_export_clipboard
from lrcmake import shared

@Gtk.Template(resource_path='/io/github/dzheremi2/lrcmake-gtk/gtk/window.ui')
class LrcmakeWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'LrcmakeWindow'

    # Main Window
    source_selection_button: Gtk.MenuButton = Gtk.Template.Child()
    music_lib: Gtk.FlowBox = Gtk.Template.Child()
    nav_view: Adw.NavigationView = Gtk.Template.Child()
    sort_revealer: Gtk.Revealer = Gtk.Template.Child()
    sorting_menu: Gtk.MenuButton = Gtk.Template.Child()
    library: Adw.NavigationPage = Gtk.Template.Child()
    search_button: Gtk.ToggleButton = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    search_button_revealer: Gtk.Revealer = Gtk.Template.Child()
    sidebar_view: Adw.OverlaySplitView = Gtk.Template.Child()
    no_dir_selected: Adw.StatusPage = Gtk.Template.Child()
    music_lib_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()

    # Sync mode
    replay_line_button: Gtk.Button = Gtk. Template.Child()
    syncing: Adw.NavigationPage = Gtk.Template.Child()
    sync_page_cover: Gtk.Image = Gtk.Template.Child()
    sync_page_title: Gtk.Inscription = Gtk.Template.Child()
    sync_page_artist: Gtk.Inscription = Gtk.Template.Child()
    lyrics_lines_box: Gtk.ListBox = Gtk.Template.Child()
    add_line_button: Gtk.Button = Gtk.Template.Child()
    controls: Gtk.MediaControls = Gtk.Template.Child()
    toggle_repeat: Gtk.ToggleButton = Gtk.Template.Child()
    sync_line_button: Gtk.Button = Gtk.Template.Child()
    playing_info_button: Gtk.Button = Gtk.Template.Child()
    rew100_button: Gtk.Button = Gtk.Template.Child()
    forw100_button: Gtk.Button = Gtk.Template.Child()
    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    export_lyrics: Gtk.MenuButton = Gtk.Template.Child()

    # Quick edit dialog
    quick_edit_dialog: Adw.Dialog = Gtk.Template.Child()
    quick_edit_dialog_input: Gtk.TextView = Gtk.Template.Child()
    quick_edit_dialog_copy_button: Gtk.Button = Gtk.Template.Child()

    # Class vars
    title = None
    artist = None
    filename = None
    filepath = None
    sort_state = shared.state_schema.get_string("sorting")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Creating base actions
        self.syncing.connect('hiding', self.reset_sync_editor)
        self.add_line_button.connect('clicked', self.append_line_end)
        self.syncing.connect('showing', self.on_sync_editor_open)
        self.toggle_repeat.connect('toggled', self.do_toggle_repeat)
        self.sync_line_button.connect('clicked', self.do_sync)
        self.playing_info_button.connect('clicked', self.show_details)
        self.rew100_button.connect('clicked', self.do_100ms_rew)
        self.forw100_button.connect('clicked', self.do_100ms_forw)
        self.replay_line_button.connect('clicked', self.do_replay_line)
        self.quick_edit_dialog.connect('closed', self.reset_quick_edit_dialog)
        self.quick_edit_dialog_copy_button.connect('clicked', self.clipboard_quick_edit_dialog_input)
        self.music_lib.set_sort_func(sorting)
        self.search_bar.connect_entry(self.search_entry)
        self.search_button_revealer.set_reveal_child(self.search_button)
        self.search_entry.connect("search-changed", self.on_search_changed)

        # Showing greeting hint if no directory selected yet
        # if self.music_lib.get_child_at_index(0) == None:
        #     self.music_lib.set_property('valign', 'center')
        #     self.music_lib.set_property('homogeneous', False)
        #     self.music_lib.append(noDirSelectedGreeting())
        if self.music_lib.get_child_at_index(0) == None:
            self.music_lib_scrolled_window.set_child(self.no_dir_selected)

    # Resets sync editor to default state
    def reset_sync_editor(self, *args):
        self.lyrics_lines_box.remove_all()
        shared.selected_row = None
        self.controls.get_media_stream().stream_ended()
        self.toggle_repeat.set_active(False)
        shared.app.remove_action("add_line_below_selected")
        shared.app.remove_action("remove_selected_line")
        shared.app.remove_action("add_line_over_selected")
        shared.app.remove_action("do_sync")
        shared.app.remove_action("append_line_end")
        shared.app.remove_action("do_100ms_rew")
        shared.app.remove_action("do_100ms_forw")
        shared.app.remove_action("do_replay_line")
        self.sort_revealer.set_reveal_child(self.sorting_menu)
        self.search_button_revealer.set_reveal_child(self.search_button)

    # Appends line to the end of lines box
    def append_line_end(self, *args):
        self.lyrics_lines_box.append(syncLine())

    # Removes currently focused line from lines box
    def remove_selected_line(self, *args):
        self.lyrics_lines_box.remove(shared.selected_row)

    # Appends line before focused one
    def prepend_line(self, *args):
        if shared.selected_row in self.lyrics_lines_box:
            childs = []
            for child in self.lyrics_lines_box:
                childs.append(child)
            index = childs.index(shared.selected_row)
            if index > 0:
                self.lyrics_lines_box.insert(syncLine(), index)
            elif index == 0:
                self.lyrics_lines_box.prepend(syncLine())

    # Appends line below focused one
    def append_line(self, *args):
        if shared.selected_row in self.lyrics_lines_box:
            childs = []
            for child in self.lyrics_lines_box:
                childs.append(child)
            index = childs.index(shared.selected_row)
            self.lyrics_lines_box.insert(syncLine(), index+1)

    # Sets sync editor hotkeys
    def on_sync_editor_open(self, *args):
        shared.app.create_action("add_line_below_selected", self.append_line, ['<primary>a'])
        shared.app.create_action("remove_selected_line", self.remove_selected_line, ['<primary>d'])
        shared.app.create_action("add_line_over_selected", self.prepend_line, ['<primary><shift>a'])
        shared.app.create_action("append_line_end", self.append_line_end, ['<Alt>a'])
        shared.app.create_action("do_sync", self.do_sync, ['<Alt>Return'])
        shared.app.create_action("do_100ms_rew", self.do_100ms_rew, ['<Alt>minus'])
        shared.app.create_action("do_100ms_forw", self.do_100ms_forw, ['<Alt>equal'])
        shared.app.create_action("do_replay_line", self.do_replay_line, ['<Alt>z'])
        self.controls.get_media_stream().connect("notify::timestamp", self.on_timestamp_changed)
        self.sort_revealer.set_reveal_child(None)
        self.search_button_revealer.set_reveal_child(None)

    # Resync focused line 100ms backward
    def do_100ms_rew(self, *args):
        pattern = r'\[([^\[\]]+)\]'
        if timing_parser() >= 100:
            timestamp = timing_parser() - 100
            new_timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}]"
            replacement = fr'{new_timestamp}'
            shared.selected_row.set_text(re.sub(pattern, replacement, shared.selected_row.get_text()))
            self.controls.get_media_stream().seek(timestamp * 1000)
        else:
            replacement = fr'[00:00.000]'
            shared.selected_row.set_text(re.sub(pattern, replacement, shared.selected_row.get_text()))
            self.controls.get_media_stream().seek(0)

    # Resync focused line 100ms forward
    def do_100ms_forw(self, *args):
        pattern = r'\[([^\[\]]+)\]'
        timestamp = timing_parser() + 100
        new_timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}]"
        replacement = fr'{new_timestamp}'
        shared.selected_row.set_text(re.sub(pattern, replacement, shared.selected_row.get_text()))
        self.controls.get_media_stream().seek(timestamp * 1000)

    # Sync or Resync focused line timestamp
    def do_sync(self, *args):
        pattern = r'\[([^\[\]]+)\] '
        timestamp = self.controls.get_media_stream().get_timestamp() // 1000
        timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}] "
        if shared.selected_row in self.lyrics_lines_box:
            childs = []
            for child in self.lyrics_lines_box:
                childs.append(child)
            index = childs.index(shared.selected_row)
        else:
            pass
        if re.search(pattern, shared.selected_row.get_text()) == None:
            shared.selected_row.set_text(timestamp + shared.selected_row.get_text())
        else:
            replacement = fr'{timestamp}'
            shared.selected_row.set_text(re.sub(pattern, replacement, shared.selected_row.get_text()))
        if self.lyrics_lines_box.get_row_at_index(index+1) != None:
            for_focus_line = self.lyrics_lines_box.get_row_at_index(index+1)
            for_focus_line.grab_focus()
        else:
            pass

    # Replays selected line
    def do_replay_line(self, *args):
        self.controls.get_media_stream().seek(timing_parser() * 1000)

    # Changing would song repeat or not
    def do_toggle_repeat(self, *args):
        if self.toggle_repeat.get_active():
            self.controls.get_media_stream().set_loop(True)
        else:
            self.controls.get_media_stream().set_loop(False)

    # Shows file details dialog
    def show_details(self, *args):
        dialog = fileDetails(title = self.title, artist = self.artist, filename = self.filename)
        dialog.properties.append(Adw.ActionRow(title = _("Loaded from Filepath"), subtitle = self.filepath, css_classes = ['property'], use_markup=False)) # type: ignore
        dialog.present(shared.win)

    # Apply highlight for line which's timestamp is lower than current song timestamp
    def on_timestamp_changed(self, media_stream, _):
        attributes = Pango.AttrList().from_string("0 -1 weight ultrabold")
        try:
            childs = []
            timestamps = []
            for child in self.lyrics_lines_box:
                child.set_attributes(None)
                if arg_timing_parser(child.get_text()) != None:
                    childs.append(child)
                    timestamps.append(arg_timing_parser(child.get_text()))
                else:
                    break
            timestamp = media_stream.get_timestamp() // 1000
            for i in range(len(timestamps) - 1):
                if timestamp >= timestamps[i] and timestamp < timestamps[i+1]:
                    childs[i].set_attributes(attributes)
                    break
                elif timestamp >= timestamps[-1]:
                    childs[-1].set_attributes(attributes)
        except (TypeError, AttributeError):
            pass

    # Action emmited when sorting method changed
    def on_sorting_action(self, action, state):
        action.set_state(state)
        self.sort_state = str(state).strip("'")
        self.music_lib.invalidate_sort()
        shared.state_schema.set_string("sorting", self.sort_state)

    # Action emmited when search filed text changed
    def on_search_changed(self, *args):
        self.music_lib.invalidate_filter()

    def show_quick_edit_dialog(self, *args):
        self.quick_edit_dialog.present(self)

    def reset_quick_edit_dialog(self, *args):
        if shared.schema.get_boolean("reset-quick-edit-on-close") == True:
            self.quick_edit_dialog_input.set_buffer(Gtk.TextBuffer().new())

    def clipboard_quick_edit_dialog_input(self, *args):
        arg_export_clipboard(
            self.quick_edit_dialog_input.get_buffer().get_text(
                start = self.quick_edit_dialog_input.get_buffer().get_start_iter(),
                end = self.quick_edit_dialog_input.get_buffer().get_end_iter(),
                include_hidden_chars = False
            )
        )