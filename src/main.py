# main.py
#
# Copyright 2024 Dzheremi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Gdk
from .window import LrcmakeWindow
from .selectData import select_file, select_dir, select_lyrics_file

app = None

class LrcmakeApplication(Adw.Application):

    win = None
    audioplayer = None

    def __init__(self):
        super().__init__(application_id='com.github.dzheremi.lrcmake',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('select_file', select_file, ['<primary>o'])
        self.create_action('select_dir', select_dir, ['<primary><shift>o'])
        self.create_action('read_from_file', select_lyrics_file)
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_resource_path("/com/github/dzheremi/lrcmake/data/icons")

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


def main(version):
    global app
    app = LrcmakeApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    main(version = "0.0.1")
