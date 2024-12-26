from gi.repository import Gtk, Adw # type: ignore
from chronograph import shared

@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/SyncLine.ui")
class SyncLine(Adw.EntryRow):
    __gtype_name__ = "SyncLine"

    def __init__(self):
        super().__init__()
        self.focus_controller = Gtk.EventControllerFocus()
        self.focus_controller.connect("enter", self.update_selected_row)
        self.add_controller(self.focus_controller)

    def update_selected_row(self, event: Gtk.EventControllerFocus):
        shared.selected_line = event.get_widget()