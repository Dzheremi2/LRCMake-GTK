from gi.repository import Gtk # type: ignore
import threading
from lrcmake import shared

def select_file(*args):
    dialog = Gtk.FileDialog(default_filter=Gtk.FileFilter(mime_types=['audio/mpeg', 'audio/basic', 'x-mpegurl', 'audio/vnd.wave']))
    dialog.open(shared.win, None, on_selected_file)

def on_selected_file(file_dialog, result):
    from lrcmake.methods.parsers import song_file_parser
    file = file_dialog.open_finish(result)
    song_file_parser(file.get_path())

def select_dir(*args):
    dialog = Gtk.FileDialog(default_filter = Gtk.FileFilter(mime_types = ['inode/directory']))
    dialog.select_folder(shared.win, None, on_selected_dir)

def on_selected_dir(file_dialog, result):
    from lrcmake.methods.parsers import dir_parser
    dir = file_dialog.select_folder_finish(result)
    thread = threading.Thread(target=lambda: (dir_parser(dir.get_path())))
    thread.daemon = True
    thread.start()

def select_lyrics_file(*args):
    dialog = Gtk.FileDialog(default_filter = Gtk.FileFilter(mime_types = ['text/plain']))
    dialog.open(shared.win, None, on_selected_lyrics_file)

def on_selected_lyrics_file(file_dialog, result):
    from lrcmake.methods.parsers import file_parser
    file = file_dialog.open_finish(result)
    file_parser(file.get_path())
