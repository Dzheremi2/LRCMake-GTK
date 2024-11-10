from gi.repository import Gtk
from .parsers import dir_parser

def select_file(*args):
    from . import main
    dialog = Gtk.FileDialog()
    dialog.open(main.app.win, None, on_selected_file)

def on_selected_file(file_dialog, result):
    file = file_dialog.open_finish(result)
    audiofile = eyed3.load(file.get_path())
    return file.get_path()

def select_dir(*args):
    from . import main
    dialog = Gtk.FileDialog(default_filter = Gtk.FileFilter(mime_types = ['inode/directory']))
    dialog.select_folder(main.app.win, None, on_selected_dir)

def on_selected_dir(file_dialog, result):
    dir = file_dialog.select_folder_finish(result)
    dir_parser(dir.get_path())
    return dir.get_path()
