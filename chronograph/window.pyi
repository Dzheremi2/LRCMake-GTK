from gi.repository import Adw, Gtk

from chronograph.ui.SongCard import SongCard  # type: ignore

class ChronographWindow(Adw.ApplicationWindow):
    """App window class"""

    # Status pages
    no_source_opened: Adw.StatusPage

    # Library view widgets
    navigation_view: Adw.NavigationView
    library_nav_page: Adw.NavigationPage
    overlay_split_view: Adw.OverlaySplitView
    right_buttons_revealer: Gtk.Revealer
    left_buttons_revealer: Gtk.Revealer
    search_bar: Gtk.SearchBar
    search_entry: Gtk.SearchEntry
    library_overlay: Gtk.Overlay
    library_scrolled_window: Gtk.ScrolledWindow
    library: Gtk.FlowBox

    # Syncing page widgets
    sync_navigation_page: Adw.NavigationPage
    controls: Gtk.MediaControls
    controls_shrinked: Gtk.MediaControls
    sync_page_cover: Gtk.Image = Gtk.Template.Child()
    sync_page_title: Gtk.Inscription = Gtk.Template.Child()
    sync_page_artist: Gtk.Inscription = Gtk.Template.Child()
    toggle_repeat_button: Gtk.ToggleButton = Gtk.Template.Child()
    sync_line_button: Gtk.Button = Gtk.Template.Child()
    replay_line_button: Gtk.Button = Gtk.Template.Child()
    rew100_button: Gtk.Button = Gtk.Template.Child()
    forw100_button: Gtk.Button = Gtk.Template.Child()
    info_button: Gtk.Button = Gtk.Template.Child()
    sync_lines: Gtk.ListBox = Gtk.Template.Child()
    add_line_button: Gtk.Button = Gtk.Template.Child()

    sort_state: str

    loaded_card: SongCard

    def on_toggle_sidebar_action(self, *_args) -> None: ...
    def on_toggle_search_action(self, *_args) -> None: ...
    def on_select_dir_action(self, *_args) -> None: ...
    def filtering(self, child: Gtk.FlowBoxChild) -> bool: ...
    def sorting(self, child1: Gtk.FlowBoxChild, child2: Gtk.FlowBoxChild) -> int: ...
    def on_search_changed(self, entry: Gtk.SearchEntry) -> None: ...
    def on_sort_changed(self, *_args) -> None: ...
    def on_append_line_action(self, *_args): ...
    def on_remove_selected_line_action(self, *_args): ...
    def on_prepend_selected_line_action(self, *_args): ...
    def on_append_selected_line_action(self, *_args): ...
    def on_sync_line_action(self, *_args) -> None: ...
    def on_replay_line_action(self, *_args) -> None: ...
    def on_100ms_rew_action(self, *_args) -> None: ...
    def on_100ms_forw_action(self, *_args) -> None: ...
    def on_show_file_info_action(self, *_args) -> None: ...
    def on_import_from_clipboard_action(self, *_args) -> None: ...
    def on_import_from_file_action(self, *_args) -> None: ...
