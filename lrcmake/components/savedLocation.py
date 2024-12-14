from gi.repository import Gtk, Adw # type: ignore
from lrcmake import shared

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/savedLocation.ui")
class savedLocation(Gtk.Box):
    __gtype_name__ = "savedLocation"

    title: Gtk.Label = Gtk.Template.Child()

    def __init__(self, title = ""):
        super().__init__()
        self.title.set_text(title)