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
        self.connect("changed", self.save_file_on_update)

    # Updates selected row for syncing purposes
    def update_selected_row(self, event):
        shared.selected_row = event.get_widget()

    # Saves lyrics file when line is getting updated (only if such preference is enabled)
    def save_file_on_update(self, *args):
        if shared.schema.get_boolean("auto-file-manipulation") == True:
            lyrics = ''
            for child in shared.win.lyrics_lines_box:
                lyrics = lyrics + (child.get_text() + "\n")
            lyrics = lyrics[:-1]
            if shared.state_schema.get_string("opened-dir-path") != "None":
                file = open(shared.state_schema.get_string("opened-dir-path") + "/" + shared.win.filename[:-4] + ".lrc", "w")
                file.write(lyrics)
                file.close()