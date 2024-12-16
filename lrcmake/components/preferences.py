import shutil
import yaml
import os

from gi.repository import Gtk, Adw, Gio # type: ignore
from lrcmake import shared

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/preferences.ui")
class LrcmakePreferences(Adw.PreferencesDialog): 
    __gtype_name__ = "LrcmakePreferences"

    auto_file_manipulation_switch: Adw.ExpanderRow = Gtk.Template.Child()
    auto_file_manipulation_format: Adw.ComboRow = Gtk.Template.Child()
    reset_quick_edit_on_close_switch: Adw.SwitchRow = Gtk.Template.Child()
    cache_songs_switch: Adw.ExpanderRow = Gtk.Template.Child()
    cache_songs_covers_switch: Adw.SwitchRow = Gtk.Template.Child()
    restore_session_switch: Adw.SwitchRow = Gtk.Template.Child()
    clear_cache_button: Adw.ButtonRow = Gtk.Template.Child()

    opened = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__class__.opened = True
        self.connect('closed', lambda _: self.set_opened(False))
        self.auto_file_manipulation_format.connect('notify::selected', self.update_auto_file_format_schema)
        self.cache_songs_switch.connect('notify::enable-expansion', lambda *_: (shared.schema.set_boolean("cache-covers", False)))
        self.clear_cache_button.connect('activated', self.clean_cache)

        shared.schema.bind("auto-file-manipulation", self.auto_file_manipulation_switch, "enable-expansion", Gio.SettingsBindFlags.DEFAULT)
        shared.schema.bind("reset-quick-edit-on-close", self.reset_quick_edit_on_close_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        shared.schema.bind("cache-songs", self.cache_songs_switch, "enable-expansion", Gio.SettingsBindFlags.DEFAULT)
        shared.schema.bind("cache-covers", self.cache_songs_covers_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        shared.schema.bind("restore-session", self.restore_session_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        
        if shared.schema.get_string("auto-file-format") == ".lrc":
            self.auto_file_manipulation_format.set_selected(0)
        elif shared.schema.get_string("auto-file-format") == ".txt":
            self.auto_file_manipulation_format.set_selected(1)

    # Makes possibility to open Preferences only once a time
    def set_opened(self, opened):
        self.__class__.opened = opened

    def clean_cache(self, *args):
        shutil.rmtree(str(shared.data_dir) + "/covers")
        shared.cache = {'pins': [], 'session': []}
        shared.cache_file.seek(0)
        shared.cache_file.truncate(0)
        yaml.dump(shared.cache, shared.cache_file)
        os.mkdir(str(shared.data_dir) + "/covers")
        
    # Updates user preferenced file format for automatic manipulation
    def update_auto_file_format_schema(self, *args):
        selected = self.auto_file_manipulation_format.get_selected()
        if selected == 0:
            shared.schema.set_string("auto-file-format", ".lrc")
        elif selected == 1:
            shared.schema.set_string("auto-file-format", ".txt")