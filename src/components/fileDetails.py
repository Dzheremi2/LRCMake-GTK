from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path="/com/github/dzheremi/lrcmake/gtk/components/fileDetails.ui")
class fileDetails(Adw.Dialog):
    __gtype_name__ = 'fileDetails'

    title_entry = Gtk.Template.Child()
    artist_entry = Gtk.Template.Child()
    filename_entry = Gtk.Template.Child()
    properties = Gtk.Template.Child()

    def __init__(self, title = _("No Data"), artist = _("No Data"), filename = _("No Data")):
        super().__init__()
        self.title_entry.set_subtitle(title)
        self.artist_entry.set_subtitle(artist)
        self.filename_entry.set_subtitle(filename)

