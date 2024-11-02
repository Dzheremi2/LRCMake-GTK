from gi.repository import Gtk
from gi.repository import Gio

def select_file(*args):
    dialog = Gtk.FileDialog()
    dialog.open(None, None, on_selected_file)

def on_selected_file(file_dialog, result):
    file = file_dialog.open_finish(result)
    print(file.get_path())
    return file.get_path()

def select_dir(*args):
    dialog = Gtk.FileDialog(default_filter = Gtk.FileFilter(mime_types = ['inode/directory']))
    dialog.select_folder(None, None, on_selected_dir)

def on_selected_dir(file_dialog, result):
    dir = file_dialog.select_folder_finish(result)
    print(dir.get_path())
    return dir.get_path()
