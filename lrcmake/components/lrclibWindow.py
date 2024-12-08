import requests
from gi.repository import Gtk, Adw  # type: ignore
from lrcmake.components.lrclibTrack import lrclibTrack
from lrcmake.methods.parsers import set_lyrics
from lrcmake import shared

title_str = _("Title") # type: ignore
artist_str = _("Artist") # type: ignore
duration_str = _("Duration") # type: ignore
album_str = _("Album") # type: ignore
instrumental_str = _("Is instrumental") # type: ignore
true_str = _("Yes") # type: ignore
false_str = _("No") # type: ignore

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/lrclibWindow.ui")
class lrclibWindow(Adw.Dialog):
    __gtype_name__ = "lrclibWindow"

    title_entry: Gtk.Entry = Gtk.Template.Child()
    artist_entry: Gtk.Entry = Gtk.Template.Child()
    results_list: Gtk.ListBox = Gtk.Template.Child()
    synced_lyrics_text_view: Gtk.TextView = Gtk.Template.Child()
    plain_lyrics_text_view: Gtk.TextView = Gtk.Template.Child()
    use_button: Gtk.Button = Gtk.Template.Child()
    start_search_button: Gtk.Button = Gtk.Template.Child()
    results_list_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    nothing_found_status: Adw.StatusPage = Gtk.Template.Child()
    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()

    opened = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.opened = True
        self.__class__.synced_lyrics_text_view = self.synced_lyrics_text_view
        self.__class__.plain_lyrics_text_view = self.plain_lyrics_text_view
        self.connect("closed", lambda _: self.set_opened(False))
        self.start_search_button.connect('clicked', self.search_lrclib)
        self.results_list.connect('row-selected', self.set_lyrics)
        self.use_button.connect('clicked', self.use_lyrics)

    def search_lrclib(self, *args):
        self.results_list_window.set_child(self.results_list)
        request = requests.get(url = "https://lrclib.net/api/search", params = {
            "track_name": self.title_entry.get_text(),
            "artist_name": self.artist_entry.get_text()
        })
        print(request.url)
        result = request.json()
        self.results_list.remove_all()
        if len(result) > 0:
            for item in result:
                self.results_list.append(
                    lrclibTrack(item["trackName"], item["artistName"],  # type: ignore
                        f"{title_str}: {item['trackName']}\n\
{artist_str}: {item['artistName']}\n\
{duration_str}: {item['duration']}\n\
{album_str}: {item['albumName']}\n\
{instrumental_str}: {true_str if item['instrumental'] == True else false_str}", item["syncedLyrics"], item["plainLyrics"]))
        else:
            self.results_list_window.set_child(self.nothing_found_status)

    def set_lyrics(self, listbox, row):
        result = row.get_child()
        if result.synced != None:
            self.synced_lyrics_text_view.set_buffer(Gtk.TextBuffer(text=result.synced))
        else:
            self.synced_lyrics_text_view.set_buffer(Gtk.TextBuffer().new())
            self.toast_overlay.add_toast(Adw.Toast(title=_("No synced lyrics available"))) # type: ignore
        
        if result.plain != None:
            self.plain_lyrics_text_view.set_buffer(Gtk.TextBuffer(text=result.plain))
        else:
            self.plain_lyrics_text_view.set_buffer(Gtk.TextBuffer().new())
            self.toast_overlay.add_toast(Adw.Toast(title=_("No plain lyrics available"))) # type: ignore

    def use_lyrics(self, *args):
        set_lyrics(self.synced_lyrics_text_view.get_buffer().get_text(
            start = self.synced_lyrics_text_view.get_buffer().get_start_iter(),
            end = self.synced_lyrics_text_view.get_buffer().get_end_iter(),
            include_hidden_chars = False
        ))
        self.close()

    def set_opened(self, opened):
        self.__class__.opened = opened