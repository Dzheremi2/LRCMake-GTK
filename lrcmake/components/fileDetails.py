from gi.repository import Adw, Gtk # type: ignore

from lrcmake import shared

@Gtk.Template(resource_path=shared.PREFIX + "/gtk/components/fileDetails.ui")
class fileDetails(Adw.Dialog):
    __gtype_name__ = 'fileDetails'

    title_entry: Adw.ActionRow = Gtk.Template.Child()
    artist_entry: Adw.ActionRow = Gtk.Template.Child()
    filename_entry: Adw.ActionRow = Gtk.Template.Child()
    properties: Adw.ActionRow = Gtk.Template.Child()

    def __init__(self, title = _("No Data"), artist = _("No Data"), filename = _("No Data")): # type: ignore
        super().__init__()
        self.title_entry.set_subtitle(title)
        self.artist_entry.set_subtitle(artist)
        self.filename_entry.set_subtitle(filename)

