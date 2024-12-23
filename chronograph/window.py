from gi.repository import Adw, Gio, GLib, Gtk  # type: ignore

from chronograph import shared
from chronograph.ui import SongCard
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
    right_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    left_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    library_overlay: Gtk.Overlay = Gtk.Template.Child()
    library_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    library: Gtk.FlowBox = Gtk.Template.Child()

    sort_state: str = shared.state_schema.get_string("sorting")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.search_bar.connect_entry(self.search_entry)
        self.library.set_filter_func(self.filtering)
        self.library.set_sort_func(self.sorting)
        self.search_entry.connect("search-changed", self.on_search_changed)

        if self.library.get_child_at_index(0) is None:
            self.library_scrolled_window.set_child(self.no_source_opened)

    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles sidebar of `self`"""
        self.overlay_split_view.set_show_sidebar(
            not self.overlay_split_view.get_show_sidebar()
        )

    def on_toggle_search_action(self, *_args) -> None:
        """Toggles search field of `self`"""
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

    def filtering(self, child: Gtk.FlowBoxChild) -> bool:
        """Technical function for `Gtk.FlowBox.invalidate_filter` working

        Parameters
        ----------
        child : Gtk.FlowBoxChild
            Child for determining if it should be filtered or not

        Returns
        ----------
        bool
            `True` if child should be displayed, `False` if not
        """
        try:
            card: SongCard = child.get_child()
            text = self.search_entry.get_text().lower()
            filtered = text != "" and not (
                text in card.title.lower() or text in card.artist.lower()
            )
            return not filtered
        except AttributeError:
            pass

    def sorting(self, child1: Gtk.FlowBoxChild, child2: Gtk.FlowBoxChild) -> int:
        """Technical function for `Gtk.FlowBox.invalidate_sort` working

        Parameters
        ----------
        child1 : Gtk.FlowBoxChild
            1st child for comparison
        child2 : Gtk.FlowBoxChild
            2nd child for comparison

        Returns
        ----------
        int
            `-1` if `child1` should be before `child2`, `1` if `child1` should be after `child2`
        """
        order = None
        if shared.win.sort_state == "a-z":
            order = False
        elif shared.win.sort_state == "z-a":
            order = True
        return ((child1.get_child().title > child2.get_child().title) ^ order) * 2 - 1

    def on_search_changed(self, *_args) -> None:
        """Invalidates filter for `self.library`"""
        self.library.invalidate_filter()

    def on_sorting_type_action(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        """Sets sorting state for `self.library` and invalidates sorting

        Parameters
        ----------
        action : Gio.SimpleAction
            Action which triggered this function
        state : GLib.Variant
            Current sorting state
        """
        action.set_state(state)
        self.sort_state = str(state).strip("'")
        self.library.invalidate_sort()
        shared.state_schema.set_string("sorting", self.sort_state)
