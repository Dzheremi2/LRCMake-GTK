from gi.repository import Adw, Gtk

from chronograph.ui.SongCard import SongCard  # type: ignore

class ChronographWindow(Adw.ApplicationWindow):
    """App window class"""

    # Status pages
    no_source_opened: Adw.StatusPage
    search_lrclib_status_page: Adw.StatusPage
    search_lrclib_collapsed_status_page: Adw.StatusPage
    lrclib_window_nothing_found_status: Adw.StatusPage
    lrclib_window_collapsed_nothing_found_status: Adw.StatusPage

    # Library view widgets
    toast_overlay: Adw.ToastOverlay
    navigation_view: Adw.NavigationView
    library_nav_page: Adw.NavigationPage
    overlay_split_view: Adw.OverlaySplitView
    open_source_button: Gtk.MenuButton
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
    sync_page_cover: Gtk.Image
    sync_page_title: Gtk.Inscription
    sync_page_artist: Gtk.Inscription
    toggle_repeat_button: Gtk.ToggleButton
    sync_line_button: Gtk.Button
    replay_line_button: Gtk.Button
    rew100_button: Gtk.Button
    forw100_button: Gtk.Button
    export_lyrics_button: Gtk.MenuButton
    info_button: Gtk.Button
    sync_lines: Gtk.ListBox
    add_line_button: Gtk.Button

    # LRClib window dialog widgets
    lrclib_window: Adw.Dialog
    lrclib_window_toast_overlay: Adw.ToastOverlay
    lrclib_window_main_clamp: Adw.Clamp
    lrclib_window_title_entry: Gtk.Entry
    lrclib_window_artist_entry: Gtk.Entry
    lrclib_window_results_list_window: Gtk.ScrolledWindow
    lrclib_window_results_list: Gtk.ListBox
    lrclib_window_synced_lyrics_text_view: Gtk.TextView
    lrclib_window_plain_lyrics_text_view: Gtk.TextView
    lrclib_window_collapsed_navigation_view: Adw.NavigationView
    lrclib_window_collapsed_lyrics_page: Adw.NavigationPage
    lrclib_window_collapsed_results_list_window: Gtk.ScrolledWindow
    lrclib_window_collapsed_results_list: Gtk.ListBox

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
    def on_import_from_lrclib_action(self, *_args) -> None: ...
    def on_search_lrclib_action(self, *_args) -> None: ...
    def set_lyrics(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None: ...
    def on_import_lyrics_lrclib_synced_action(self, *_args) -> None: ...
    def on_import_lyrics_lrclib_plain_action(self, *_args) -> None: ...
    def on_export_to_file_action(self, *_args) -> None: ...
    def on_export_to_clipboard_action(self, *_args) -> None: ...
    def on_export_to_lrclib_action(self, *_args) -> None: ...
    def on_show_preferences_action(self, *args) -> None: ...
