from gi.repository import Gdk, Adw, Gtk

import re
from lrcmake.methods.parsers import arg_line_parser
from lrcmake import shared

# Exports data to user's clipbaord
def export_clipboard(*args):
    clipboard = Gdk.Display.get_default().get_clipboard()
    lyrics = ''
    for child in shared.win.lyrics_lines_box:
        lyrics = lyrics + (child.get_text() + "\n")
    lyrics = lyrics[:-1]
    clipboard.set(lyrics)

# Return string with synced lyrics for publishing
def prepare_synced_lyrics():
    lyrics = ''
    for child in shared.win.lyrics_lines_box:
        if arg_line_parser(child.get_text()) != None:
            lyrics = lyrics + (child.get_text() + "\n")
        else:
            shared.win.export_lyrics.set_icon_name("export-to-symbolic")
            toast = Adw.Toast(title=_("Seems like not every line is synced!"))
            shared.win.toast_overlay.add_toast(toast)
            raise IndexError("Not all lines have timestamps")
    lyrics = lyrics[:-1]
    return lyrics

# Return string with plain lyrics for publishing
def prepare_plain_lyrics():
    pattern = r'\[.*?\] '
    plain_lyrics = []
    for child in shared.win.lyrics_lines_box:
        plain_lyrics.append(re.sub(pattern, "", child.get_text()))
    return "\n".join(plain_lyrics[:-1])

def export_file(*args):
    dialog = Gtk.FileDialog(initial_name=shared.win.title + " - " + shared.win.artist + ".lrc")
    dialog.save(shared.win, None, on_export_file)

def on_export_file(file_dialog, result):
    lyrics = prepare_synced_lyrics()
    filepath = file_dialog.save_finish(result).get_path()
    file = open(filepath, 'w')
    file.write(lyrics)
    file.close()