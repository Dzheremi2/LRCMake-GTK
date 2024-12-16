import os
import sys
import gi
import threading
import yaml

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Gdk, GLib # type: ignore
from lrcmake.window import LrcmakeWindow
from lrcmake.components.preferences import LrcmakePreferences
from lrcmake.components.lrclibWindow import lrclibWindow
from lrcmake.methods.selectData import select_file, select_dir, select_lyrics_file, import_lyrics_lrclib_synced, import_lyrics_lrclib_plain
from lrcmake.methods.parsers import clipboard_parser, filtering
from lrcmake.methods.exportData import export_clipboard, export_file
from lrcmake.methods.publish import do_publish
from lrcmake import shared

class LrcmakeApplication(Adw.Application):
    def __init__(self):
        # Create basic actions and resources
        super().__init__(application_id=shared.APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('select_file', select_file, ['<primary>o'])
        self.create_action('select_dir', select_dir, ['<primary><shift>o'])
        self.create_action('read_from_clipboard', clipboard_parser)
        self.create_action('read_from_file', select_lyrics_file)
        self.create_action('export_to_clipboard', export_clipboard)
        self.create_action("export_to_lrclib", self.async_do_publish)
        self.create_action("export_to_file", export_file)
        self.create_action('about_app', self.show_about_dialog)
        self.create_action("toggle_search", self.toggle_search, ['<primary>f'])
        self.create_action('open_lrclib_search', self.show_lrclibWindow)
        self.create_action('show_sidebar', self.show_sidebar)
        self.create_action("show_preferences", self.show_preferences, ['<primary>comma'])
        self.create_action('import_lyrics_lrclib_synced', import_lyrics_lrclib_synced)
        self.create_action('import_lyrics_lrclib_plain', import_lyrics_lrclib_plain)
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_resource_path(shared.PREFIX + "/data/icons")

    # Emmits when app is activated
    def do_activate(self):
        win = self.props.active_window
        if not win:
            shared.win = win = LrcmakeWindow(application=self)
        shared.win.present()
        sorting_action = Gio.SimpleAction.new_stateful(
            "sort_type",
            GLib.VariantType.new("s"),
            sorting_mode := GLib.Variant("s", shared.state_schema.get_string("sorting"))
        )
        sorting_action.connect("activate", shared.win.on_sorting_action)
        self.add_action(sorting_action)
        shared.win.music_lib.set_filter_func(filtering)
        self.create_action('open_quick_edit', shared.win.show_quick_edit_dialog)

    # Emmits when app is closed
    def do_shutdown(self):
        shared.state_schema.set_string("opened-dir-path", "None")
        print("Exited")

    # Used for creating new actions
    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    # Creates thread for publishing on LRCLIB
    def async_do_publish(self, *args):
        thread = threading.Thread(target=do_publish)
        thread.daemon = True
        thread.start()
        shared.win.export_lyrics.set_child(Gtk.Spinner(spinning=True))

    # Shows preferences dialog
    def show_preferences(self, *args):
        if LrcmakePreferences.opened:
            return
        preferences = LrcmakePreferences()
        preferences.present(shared.win)

    # Shows main window
    def show_lrclibWindow(self, *args):
        if lrclibWindow.opened:
            return
        self.lrclib_searcher = lrclibWindow()
        self.lrclib_searcher.present(shared.win)

    # Shows saves sidebar
    def show_sidebar(self, *args):
        if shared.win.sidebar_view.get_show_sidebar():
            shared.win.sidebar_view.set_show_sidebar(False)
        else:
            shared.win.sidebar_view.set_show_sidebar(True)

    # Controls when search must be visible and when not
    def toggle_search(self, *args):
        if shared.win.nav_view.get_visible_page() == shared.win.library:
            search_bar = shared.win.search_bar
            search_entry = shared.win.search_entry
        else:
            return
        search_bar.set_search_mode(not (search_mode := search_bar.get_search_mode()))

        if not search_mode:
            shared.win.set_focus(search_entry)
        search_entry.set_text("")

    # Shows About App dialog
    def show_about_dialog(self, *args):
        dialog = Adw.AboutDialog.new_from_appdata(shared.PREFIX + "/" + shared.APP_ID + ".metainfo.xml", shared.VERSION)
        dialog.set_version(shared.VERSION)
        dialog.set_developers(
            (
                "Dzheremi https://github.com/Dzheremi2",
            )
        )
        dialog.set_designers(("Dzheremi",))
        dialog.set_translator_credits(_("Thanks for all translators on Hosted Weblate! https://hosted.weblate.org/projects/lrcmake/lrcmake/")) # type: ignore
        dialog.set_copyright("© 2024 Dzheremi")
        dialog.add_legal_section(
            "LRClib",
            "",
            Gtk.License.MIT_X11
        )
        dialog.present(shared.win)

# App's Entry point
def main(_version):
    if not ("cache.yaml" in os.listdir(shared.data_dir)):
        file = open(str(shared.data_dir) + "/cache.yaml", "x")
        file.write("pins:")
        file.close()

    if not("covers" in os.listdir(shared.data_dir)):
        os.mkdir(str(shared.data_dir) + "/covers")

    shared.cache_file = open(str(shared.data_dir) + "/cache.yaml", "r+", encoding='utf-8')
    shared.cache = yaml.safe_load(shared.cache_file)
    shared.app = app = LrcmakeApplication()
    return app.run(sys.argv)