from gi.repository import Gtk

@Gtk.Template(resource_path="/com/github/dzheremi/lrcmake/gtk/components/syncLine.ui")
class syncLine(Adw.EntryRow):
     __gtype_name__ = 'syncLine'

    def __init__(self, text = ""):
        super().__init__()
