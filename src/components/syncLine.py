from gi.repository import Gtk
from gi.repository import Adw
from . import shared
from . import main

@Gtk.Template(resource_path="/com/github/dzheremi/lrcmake/gtk/components/syncLine.ui")
class syncLine(Adw.EntryRow):
    __gtype_name__ = 'syncLine'

    def __init__(self, *args):
        super().__init__(*args)
        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect('enter', self.update_selected_row)
        self.add_controller(self.focus_controller)

    def update_selected_row(self, event):
        shared.shared.selected_row = event.get_widget()
