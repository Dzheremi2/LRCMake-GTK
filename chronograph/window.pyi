from gi.repository import Adw, Gtk  # type: ignore

class ChronographWindow(Adw.ApplicationWindow):
    """App window class

    GTK Objects
    ----------
    ::

        # Status pages
        no_source_opened: Adw.StatusPage -> Status page> displayed when no items in library

        # Library view widgets
        navigation_view: Adw.NavigationView -> Main Navigation view
        library_nav_page: Adw.NavigationPage -> Library Navigation page
        overlay_split_view: Adw.OverlaySplitView -> Split view for Sidebar and Library
        search_bar: Gtk.SearchBar -> Search bar
        search_entry: Gtk.SearchEntry -> Search field
        library_overlay: Gtk.Overlay -> Library overlay
        library_scrolled_window: Gtk.ScrolledWindow -> Library scroll possibility
        library: Gtk.FlowBox -> Library itself
    """
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
    
    def on_toggle_sidebar_action(self, *_args) -> None: ...
    def on_toggle_search_action(self, *_args) -> None: ...
    def on_select_dir_action(self, *_args) -> None: ...
    def filtering(self, child: Gtk.FlowBoxChild) -> bool: ...
    def sorting(self, child1: Gtk.FlowBoxChild, child2: Gtk.FlowBoxChild) -> int: ...
    def on_search_changed(self, entry: Gtk.SearchEntry) -> None: ...
    def on_sort_changed(self, *_args) -> None: ...
