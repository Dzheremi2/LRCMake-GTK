from gi.repository import Gtk, Adw # type: ignore

from lrcmake import shared

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/lrclibTrack.ui")
class lrclibTrack(Gtk.Box):
    __gtype_name__ = "lrclibTrack"

    title_label: Gtk.Inscription = Gtk.Template.Child()
    artist_label: Gtk.Inscription = Gtk.Template.Child()

    def __init__(self, title = "Unknown", artist = "Unknown", tooltip_text = "", synced = "", plain = ""):
        super().__init__()
        self.title_label.set_text(title)
        self.artist_label.set_text(artist)
        self.set_tooltip_text(tooltip_text)
        self.synced = synced
        self.plain = plain