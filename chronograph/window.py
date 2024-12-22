from gi.repository import Adw, Gtk  # type: ignore

from chronograph import shared
from chronograph.utils.select_data import select_dir


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
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

    __gtype_name__ = "ChronographWindow"

    # Status pages
    no_source_opened: Adw.StatusPage = Gtk.Template.Child()

    # Library view widgets
    navigation_view: Adw.NavigationView = Gtk.Template.Child()
    library_nav_page: Adw.NavigationPage = Gtk.Template.Child()
    overlay_split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    library_overlay: Gtk.Overlay = Gtk.Template.Child()
    library_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    library: Gtk.FlowBox = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.search_bar.connect_entry(self.search_entry)

        if self.library.get_child_at_index(0) is None:
            self.library_scrolled_window.set_child(self.no_source_opened)

    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles sidebar of `ChronographWindow`"""
        self.overlay_split_view.set_show_sidebar(
            not self.overlay_split_view.get_show_sidebar()
        )

    def on_toggle_search_action(self, *_args) -> None:
        """Toggles search filed of `ChronographWindow`"""
        if self.navigation_view.get_visible_page() == self.library_nav_page:
            search_bar = self.search_bar
            search_entry = self.search_entry
        else:
            return

        search_bar.set_search_mode(not (search_mode := search_bar.get_search_mode()))

        if not search_mode:
            self.set_focus(search_entry)

        search_entry.set_text("")

    def on_select_dir_action(self, *_args) -> None:
        """Creates directory selection dialog for adding Songs to `self.library`"""
        select_dir()
