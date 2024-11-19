from gi.repository import Gdk, Adw

import re
from .parsers import arg_line_parser
from . import main

def export_clipboard(*args):
    clipboard = Gdk.Display.get_default().get_clipboard()
    lyrics = ''
    for child in main.app.win.lyrics_lines_box:
        lyrics = lyrics + (child.get_text() + "\n")
    lyrics = lyrics[:-1]
    clipboard.set(lyrics)

def prepare_synced_lyrics():
    lyrics = ''
    for child in main.app.win.lyrics_lines_box:
        if arg_line_parser(child.get_text()) != None:
            lyrics = lyrics + (child.get_text() + "\n")
        else:
            main.app.win.export_lyrics.set_icon_name("export-to-symbolic")
            toast = Adw.Toast(title=_("Seems like not every line is synced!"))
            main.app.win.toast_overlay.add_toast(toast)
            raise IndexError("Not all lines have timestamps")
    lyrics = lyrics[:-1]
    return lyrics

def prepare_plain_lyrics():
    pattern = r'\[.*?\] '
    plain_lyrics = []
    for child in main.app.win.lyrics_lines_box:
        plain_lyrics.append(re.sub(pattern, "", child.get_text()))
    return "\n".join(plain_lyrics[:-1])