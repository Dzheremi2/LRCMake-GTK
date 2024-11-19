import sys
import gi
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Gdk, GLib
from .window import LrcmakeWindow
from .selectData import select_file, select_dir, select_lyrics_file
from .parsers import clipboard_parser
from .exportData import export_clipboard
from .publish import do_publish

app = None

class LrcmakeApplication(Adw.Application):

    win = None
    audioplayer = None

    def __init__(self, version):
        super().__init__(application_id='io.github.dzheremi2.lrcmake-gtk',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.version = version
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('select_file', select_file, ['<primary>o'])
        self.create_action('select_dir', select_dir, ['<primary><shift>o'])
        self.create_action('read_from_clipboard', clipboard_parser)
        self.create_action('read_from_file', select_lyrics_file)
        self.create_action('export_to_clipboard', export_clipboard)
        self.create_action("export_to_lrclib", self.async_do_publish)
        self.create_action('about_app', self.show_about_dialog)
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_resource_path("/io/github/dzheremi2/lrcmake-gtk/data/icons")

    def do_activate(self):
        win = self.props.active_window
        if not self.win:
            self.win = LrcmakeWindow(application=self)
        self.win.present()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def async_do_publish(self, *args):
        thread = threading.Thread(target=do_publish)
        thread.daemon = True
        thread.start()
        self.win.export_lyrics.set_child(Gtk.Spinner(spinning=True))

    def show_about_dialog(self, *args):
        dialog = Adw.AboutDialog(
            application_icon="io.github.dzheremi2.lrcmake-gtk",
            application_name="LRCMake",
            developer_name="Dzheremi",
            issue_url="https://github.com/Dzheremi2/LRCMake-GTK/issues",
            license="GNU GPL V3 OR LATER",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/Dzheremi2/LRCMake-GTK",
            version=self.version,
            designers=["Dzheremi"]
        )
        dialog.present(self.win)

def main(version):
    global app
    app = LrcmakeApplication(version)
    return app.run(sys.argv)