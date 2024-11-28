from gi.repository import Gtk, Adw, Gio
from lrcmake import shared

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/preferences.ui")
class LrcmakePreferences(Adw.PreferencesDialog): 
    __gtype_name__ = "LrcmakePreferences"

    auto_file_manipulation_switch: Adw.SwitchRow = Gtk.Template.Child()

    opened = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__class__.opened = True
        self.connect("closed", lambda _: self.set_opened(False))

        shared.schema.bind("auto-file-manipulation", getattr(self, "auto_file_manipulation_switch"), "active", Gio.SettingsBindFlags.DEFAULT)

    # Makes possibility to open Preferences only once a time
    def set_opened(self, opened):
        self.__class__.opened = opened