from gi.repository import Gtk, Adw # type: ignore
from lrcmake import shared

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/savedLocation.ui")
class savedLocation(Gtk.Box):
    __gtype_name__ = "savedLocation"

    title: Gtk.Label = Gtk.Template.Child()

    def __init__(self, path, title = "", tooltip_text = ""):
        super().__init__()
        self.path = path
        self.title.set_text(title)
        self.set_tooltip_text(tooltip_text)

    def get_path(self):
        return self.path