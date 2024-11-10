from gi.repository import Gdk

from . import main

def export_clipboard(*args):
    clipboard = Gdk.Display.get_default().get_clipboard()
    lyrics = ''
    for child in main.app.win.lyrics_lines_box:
        lyrics = lyrics + (child.get_text() + "\n")
    lyrics = lyrics[:-1]
    clipboard.set(lyrics)
