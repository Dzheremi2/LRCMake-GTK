from gi.repository import Gtk
from gi.repository import Adw
from lrcmake import shared

@Gtk.Template(resource_path=shared.PREFIX + "/gtk/components/syncLine.ui")
class syncLine(Adw.EntryRow):
    __gtype_name__ = 'syncLine'

    def __init__(self, *args):
        super().__init__()
        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.update_selected_row)
        self.add_controller(self.focus_controller)

    def update_selected_row(self, event):
        shared.selected_row = event.get_widget()
