import re
import threading

import requests
from gi.repository import Adw, Gio, GLib, Gtk  # type: ignore

from chronograph import shared
from chronograph.ui.BoxDialog import BoxDialog
from chronograph.ui.LrclibTrack import LrclibTrack
from chronograph.ui.SongCard import (
    SongCard,
    album_str,
    artist_str,
    label_str,
    path_str,
    title_str,
)
from chronograph.ui.SyncLine import SyncLine
from chronograph.utils.export_data import export_clipboard, export_file
from chronograph.utils.parsers import (
    clipboard_parser,
    line_parser,
    string_parser,
    sync_lines_parser,
    timing_parser,
)
from chronograph.utils.publish import do_publish
from chronograph.utils.select_data import select_dir, select_lyrics_file


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class ChronographWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "ChronographWindow"

    # Status pages
    no_source_opened: Adw.StatusPage = Gtk.Template.Child()
    search_lrclib_status_page: Adw.StatusPage = Gtk.Template.Child()
    search_lrclib_collapsed_status_page: Adw.StatusPage = Gtk.Template.Child()
    lrclib_window_nothing_found_status: Adw.StatusPage = Gtk.Template.Child()
    lrclib_window_collapsed_nothing_found_status: Adw.StatusPage = Gtk.Template.Child()

    # Library view widgets
    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    navigation_view: Adw.NavigationView = Gtk.Template.Child()
    library_nav_page: Adw.NavigationPage = Gtk.Template.Child()
    overlay_split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    open_source_button: Gtk.MenuButton = Gtk.Template.Child()
    right_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    left_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    library_overlay: Gtk.Overlay = Gtk.Template.Child()
    library_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    library: Gtk.FlowBox = Gtk.Template.Child()

    # Syncing page widgets
    sync_navigation_page: Adw.NavigationPage = Gtk.Template.Child()
    controls: Gtk.MediaControls = Gtk.Template.Child()
    controls_shrinked: Gtk.MediaControls = Gtk.Template.Child()
    sync_page_cover: Gtk.Image = Gtk.Template.Child()
    sync_page_title: Gtk.Inscription = Gtk.Template.Child()
    sync_page_artist: Gtk.Inscription = Gtk.Template.Child()
    toggle_repeat_button: Gtk.ToggleButton = Gtk.Template.Child()
    sync_line_button: Gtk.Button = Gtk.Template.Child()
    replay_line_button: Gtk.Button = Gtk.Template.Child()
    rew100_button: Gtk.Button = Gtk.Template.Child()
    forw100_button: Gtk.Button = Gtk.Template.Child()
    export_lyrics_button: Gtk.MenuButton = Gtk.Template.Child()
    info_button: Gtk.Button = Gtk.Template.Child()
    sync_lines: Gtk.ListBox = Gtk.Template.Child()
    add_line_button: Gtk.Button = Gtk.Template.Child()

    # LRClib window dialog widgets
    lrclib_window: Adw.Dialog = Gtk.Template.Child()
    lrclib_window_toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    lrclib_window_main_clamp: Adw.Clamp = Gtk.Template.Child()
    lrclib_window_title_entry: Gtk.Entry = Gtk.Template.Child()
    lrclib_window_artist_entry: Gtk.Entry = Gtk.Template.Child()
    lrclib_window_results_list_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    lrclib_window_results_list: Gtk.ListBox = Gtk.Template.Child()
    lrclib_window_synced_lyrics_text_view: Gtk.TextView = Gtk.Template.Child()
    lrclib_window_plain_lyrics_text_view: Gtk.TextView = Gtk.Template.Child()
    lrclib_window_collapsed_navigation_view: Adw.NavigationView = Gtk.Template.Child()
    lrclib_window_collapsed_lyrics_page: Adw.NavigationPage = Gtk.Template.Child()
    lrclib_window_collapsed_results_list_window: Gtk.ScrolledWindow = (
        Gtk.Template.Child()
    )
    lrclib_window_collapsed_results_list: Gtk.ListBox = Gtk.Template.Child()

    sort_state: str = shared.state_schema.get_string("sorting")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.loaded_card: SongCard = None

        self.search_bar.connect_entry(self.search_entry)
        self.library.set_filter_func(self.filtering)
        self.library.set_sort_func(self.sorting)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.lrclib_window_results_list.connect("row-selected", self.set_lyrics)
        self.lrclib_window_collapsed_results_list.connect(
            "row-selected", self.set_lyrics
        )

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

    def on_show_file_info_action(self, *_args) -> None:
        """Creates dialog with information about selected file"""
        BoxDialog(
            label_str,
            (
                (title_str, self.loaded_card.title),
                (artist_str, self.loaded_card.artist),
                (album_str, self.loaded_card.album),
                (path_str, self.loaded_card._file.path),
            ),
        ).present(self)

    def on_append_line_action(self, *_args) -> None:
        """Appends new `SyncLine` to `self.sync_lines`"""
        self.sync_lines.append(SyncLine())

    def on_remove_selected_line_action(self, *_args) -> None:
        """Removes selected `SyncLine` from `self.sync_lines`"""
        lines = []
        for line in self.sync_lines:
            lines.append(line)
        index = lines.index(shared.selected_line)
        self.sync_lines.remove(shared.selected_line)
        self.sync_lines.get_row_at_index(index).grab_focus()

    def on_prepend_selected_line_action(self, *_args) -> None:
        """Prepends new `SyncLine` before selected `SyncLine` in `self.sync_lines`"""
        if shared.selected_line in self.sync_lines:
            childs = []
            for child in self.sync_lines:
                childs.append(child)
            index = childs.index(shared.selected_line)
            if index > 0:
                self.sync_lines.insert(SyncLine(), index)
            elif index == 0:
                self.sync_lines.prepend(SyncLine())

    def on_append_selected_line_action(self, *_args) -> None:
        """Appends new `SyncLine` after selected `SyncLine` in `self.sync_lines`"""
        if shared.selected_line in self.sync_lines:
            childs = []
            for child in self.sync_lines:
                childs.append(child)
            index = childs.index(shared.selected_line)
            self.sync_lines.insert(SyncLine(), index + 1)

    def on_sync_line_action(self, *_args) -> None:
        """Syncs selected `SyncLine` with current media stream timestamp"""
        pattern = r"\[([^\[\]]+)\] "
        timestamp = self.controls.get_media_stream().get_timestamp() // 1000
        timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}] "
        if shared.selected_line in self.sync_lines:
            childs = []
            for child in self.sync_lines:
                childs.append(child)
            index = childs.index(shared.selected_line)
        else:
            pass

        if re.search(pattern, shared.selected_line.get_text()) is None:
            shared.selected_line.set_text(timestamp + shared.selected_line.get_text())
        else:
            replacement = rf"{timestamp}"
            shared.selected_line.set_text(
                re.sub(pattern, replacement, shared.selected_line.get_text())
            )

        if (indexed_row := self.sync_lines.get_row_at_index(index + 1)) is not None:
            indexed_row.grab_focus()
        else:
            pass

    def on_replay_line_action(self, *_args) -> None:
        """Replays selected `SyncLine` for its timestamp"""
        self.controls.get_media_stream().seek(
            timing_parser(shared.selected_line.get_text()) * 1000
        )

    def on_100ms_rew_action(self, *_args) -> None:
        """Rewinds media stream for 100ms from selected `SyncLine` timestamp and resync itself timestamp"""
        pattern = r"\[([^\[\]]+)\]"
        if (
            line_timestamp_prefix := timing_parser(shared.selected_line.get_text())
        ) >= 100:
            timestamp = line_timestamp_prefix - 100
            new_timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}]"
            replacement = rf"{new_timestamp}"
            shared.selected_line.set_text(
                re.sub(pattern, replacement, shared.selected_line.get_text())
            )
            self.controls.get_media_stream().seek(timestamp * 1000)
        else:
            replacement = rf"[00:00.000]"
            shared.selected_line.set_text(
                re.sub(pattern, replacement, shared.selected_line.get_text())
            )
            self.controls.get_media_stream().seek(0)

    def on_100ms_forw_action(self, *_args) -> None:
        """Forwards media stream for 100ms from selected `SyncLine` timestamp and resync itself timestamp"""
        timestamp = timing_parser(shared.selected_line.get_text()) + 100
        new_timestamp = f"[{timestamp // 60000:02d}:{(timestamp % 60000) // 1000:02d}.{timestamp % 1000:03d}]"
        shared.selected_line.set_text(
            re.sub(
                r"\[([^\[\]]+)\]", rf"{new_timestamp}", shared.selected_line.get_text()
            )
        )
        self.controls.get_media_stream().seek(timestamp * 1000)

    def on_import_from_clipboard_action(self, *_args) -> None:
        """Imports text from clipboard to `self.sync_lines`"""
        clipboard_parser()

    def on_import_from_file_action(self, *_args) -> None:
        """Imports text from file to `self.sync_lines`"""
        select_lyrics_file()

    def on_import_from_lrclib_action(self, *_args) -> None:
        """Presents `self.lrclib_window` dialog"""
        self.lrclib_window_artist_entry.set_buffer(Gtk.EntryBuffer())
        self.lrclib_window_title_entry.set_buffer(Gtk.EntryBuffer())
        self.lrclib_window_results_list.remove_all()
        self.lrclib_window_results_list_window.set_child(self.search_lrclib_status_page)
        self.lrclib_window_synced_lyrics_text_view.set_buffer(Gtk.TextBuffer.new())
        self.lrclib_window_plain_lyrics_text_view.set_buffer(Gtk.TextBuffer.new())
        self.lrclib_window_collapsed_results_list.remove_all()
        self.lrclib_window_collapsed_results_list_window.set_child(
            self.search_lrclib_collapsed_status_page
        )
        self.lrclib_window.present(self)

    def on_search_lrclib_action(self, *_args) -> None:
        """Parses LRclib for tracks with Title and Artist from `self.lrclib_window_title_entry` and `self.lrclib_window_artist_entry`"""
        request: requests.Response = requests.get(
            url="https://lrclib.net/api/search",
            params={
                "track_name": self.lrclib_window_title_entry.get_text(),
                "artist_name": self.lrclib_window_artist_entry.get_text(),
            },
        )
        print(request.url)
        result = request.json()
        self.lrclib_window_results_list.remove_all()
        self.lrclib_window_collapsed_results_list.remove_all()
        if len(result) > 0:
            for item in result:
                self.lrclib_window_results_list.append(
                    LrclibTrack(
                        title=item["trackName"],
                        artist=item["artistName"],
                        tooltip=(
                            item["trackName"],
                            item["artistName"],
                            item["duration"],
                            item["albumName"],
                            item["instrumental"],
                        ),
                        synced=item["syncedLyrics"],
                        plain=item["plainLyrics"],
                    )
                )
                self.lrclib_window_collapsed_results_list.append(
                    LrclibTrack(
                        title=item["trackName"],
                        artist=item["artistName"],
                        tooltip=(
                            item["trackName"],
                            item["artistName"],
                            item["duration"],
                            item["albumName"],
                            item["instrumental"],
                        ),
                        synced=item["syncedLyrics"],
                        plain=item["plainLyrics"],
                    )
                )
            self.lrclib_window_results_list_window.set_child(
                self.lrclib_window_results_list
            )
            self.lrclib_window_collapsed_results_list_window.set_child(
                self.lrclib_window_collapsed_results_list
            )
        else:
            self.lrclib_window_results_list_window.set_child(
                self.lrclib_window_nothing_found_status
            )
            self.lrclib_window_collapsed_results_list_window.set_child(
                self.lrclib_window_collapsed_nothing_found_status
            )

    def set_lyrics(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Triggers `chronograph.ui.LrclibTrack.set_lyrics`

        Parameters
        ----------
        _listbox : Gtk.ListBox
            garbage parameter
        row : Gtk.ListBoxRow
            `Gtk.ListBoxRow` to claim `LrclibTrack` from
        """
        row.get_child().set_lyrics()

    def on_import_lyrics_lrclib_synced_action(self, *_args) -> None:
        """Import synced lyrics from LRCLib to `self.sync_lines`"""
        string_parser(
            self.lrclib_window_synced_lyrics_text_view.get_buffer().get_text(
                start=self.lrclib_window_synced_lyrics_text_view.get_buffer().get_start_iter(),
                end=self.lrclib_window_synced_lyrics_text_view.get_buffer().get_end_iter(),
                include_hidden_chars=False,
            )
        )
        self.lrclib_window.close()

    def on_import_lyrics_lrclib_plain_action(self, *_args) -> None:
        """Import plain lyrics from LRCLib to `self.sync_lines`"""
        string_parser(
            self.lrclib_window_plain_lyrics_text_view.get_buffer().get_text(
                start=self.lrclib_window_plain_lyrics_text_view.get_buffer().get_start_iter(),
                end=self.lrclib_window_plain_lyrics_text_view.get_buffer().get_end_iter(),
                include_hidden_chars=False,
            )
        )
        self.lrclib_window.close()

    def on_export_to_file_action(self, *_args) -> None:
        """Exports current `self.sync_lines` lyrics to file"""
        export_file(sync_lines_parser())

    def on_export_to_clipboard_action(self, *_args) -> None:
        """Exports current `self.sync_lines` lyrics to clipbaord"""
        export_clipboard(sync_lines_parser())

    def on_export_to_lrclib_action(self, *_args) -> None:
        thread = threading.Thread(target=do_publish)
        thread.daemon = True
        thread.start()
        shared.win.export_lyrics_button.set_child(Adw.Spinner())
