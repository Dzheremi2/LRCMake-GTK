from gi.repository import Gtk

def select_file(*args):
    from lrcmake import shared
    dialog = Gtk.FileDialog(default_filter=Gtk.FileFilter(mime_types=['audio/mpeg', 'audio/basic', 'x-mpegurl', 'audio/vnd.wave']))
    dialog.open(shared.win, None, on_selected_file)

def on_selected_file(file_dialog, result):
    from lrcmake.methods.parsers import song_file_parser
    file = file_dialog.open_finish(result)
    song_file_parser(file.get_path())

def select_dir(*args):
    from lrcmake import shared
    dialog = Gtk.FileDialog(default_filter = Gtk.FileFilter(mime_types = ['inode/directory']))
    dialog.select_folder(shared.win, None, on_selected_dir)

def on_selected_dir(file_dialog, result):
    from lrcmake.methods.parsers import dir_parser
    dir = file_dialog.select_folder_finish(result)
    dir_parser(dir.get_path())

def select_lyrics_file(*args):
    from lrcmake import shared
    dialog = Gtk.FileDialog(default_filter = Gtk.FileFilter(mime_types = ['text/plain']))
    dialog.open(shared.win, None, on_selected_lyrics_file)

def on_selected_lyrics_file(file_dialog, result):
    from lrcmake.methods.parsers import file_parser
    file = file_dialog.open_finish(result)
    file_parser(file.get_path())
