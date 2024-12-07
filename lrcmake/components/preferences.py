from gi.repository import Gtk, Adw, Gio # type: ignore
from lrcmake import shared

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/preferences.ui")
class LrcmakePreferences(Adw.PreferencesDialog): 
    __gtype_name__ = "LrcmakePreferences"

    auto_file_manipulation_switch: Adw.ExpanderRow = Gtk.Template.Child()
    auto_file_manipulation_format: Adw.ComboRow = Gtk.Template.Child()
    reset_quick_edit_on_close_switch: Adw.SwitchRow = Gtk.Template.Child()

    opened = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__class__.opened = True
        self.connect("closed", lambda _: self.set_opened(False))
        self.auto_file_manipulation_format.connect("notify::selected", self.update_auto_file_format_schema)

        shared.schema.bind("auto-file-manipulation", self.auto_file_manipulation_switch, "enable-expansion", Gio.SettingsBindFlags.DEFAULT)
        shared.schema.bind("reset-quick-edit-on-close", self.reset_quick_edit_on_close_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        if shared.schema.get_string("auto-file-format") == ".lrc":
            self.auto_file_manipulation_format.set_selected(0)
        elif shared.schema.get_string("auto-file-format") == ".txt":
            self.auto_file_manipulation_format.set_selected(1)

    # Makes possibility to open Preferences only once a time
    def set_opened(self, opened):
        self.__class__.opened = opened

    # Updates user preferenced file format for automatic manipulation
    def update_auto_file_format_schema(self, *args):
        selected = self.auto_file_manipulation_format.get_selected()
        if selected == 0:
            shared.schema.set_string("auto-file-format", ".lrc")
        elif selected == 1:
            shared.schema.set_string("auto-file-format", ".txt")