from gi.repository import Adw, Gtk  # type: ignore

from chronograph import shared
from chronograph.ui.SongCard import SongCard
from chronograph.utils.file_mutagen_id3 import FileID3
from chronograph.utils.file_mutagen_vorbis import FileVorbis


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class ChronographWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "ChronographWindow"

    # Status pages
    no_source_opened: Adw.StatusPage = Gtk.Template.Child()

    # Library view widgets
    navigation_view: Adw.NavigationView = Gtk.Template.Child()
    library_nav_page: Adw.NavigationPage = Gtk.Template.Child()
    overlay_split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    library_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    library: Gtk.FlowBox = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.search_bar.connect_entry(self.search_entry)
        self.library.append(
            SongCard(
                FileVorbis("/home/dzheremi/Music/Symphony No.6 (1st movement).flac")
            )
        )

        if self.library.get_child_at_index(0) is None:
            self.library_scrolled_window.set_child(self.no_source_opened)

    def on_toggle_sidebar_action(self, *_args) -> None:
        value = not self.overlay_split_view.get_show_sidebar()
        self.overlay_split_view.set_show_sidebar(value)

    def on_toggle_search_action(self, *_args) -> None:
        if self.navigation_view.get_visible_page() == self.library_nav_page:
            search_bar = self.search_bar
            search_entry = self.search_entry
        else:
            return

        search_bar.set_search_mode(not (search_mode := search_bar.get_search_mode))

        if not search_mode:
            self.set_focus(search_entry)

        search_entry.set_text("")
