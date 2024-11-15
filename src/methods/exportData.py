from gi.repository import Gdk

import re
from . import main

def export_clipboard(*args):
    clipboard = Gdk.Display.get_default().get_clipboard()
    lyrics = ''
    for child in main.app.win.lyrics_lines_box:
        lyrics = lyrics + (child.get_text() + "\n")
    lyrics = lyrics[:-1]
    clipboard.set(lyrics)

def prepare_synced_lyrics(*args):
    lyrics = ''
    for child in main.app.win.lyrics_lines_box:
        lyrics = lyrics + (child.get_text() + "\n")
    lyrics = lyrics[:-1]
    return lyrics
    #print(lyrics)

def prepare_plain_lyrics(*args):
    pattern = r'\[.*?\] '
    plain_lyrics = []
    for child in main.app.win.lyrics_lines_box:
        plain_lyrics.append(re.sub(pattern, "", child.get_text()))
    return "\n".join(plain_lyrics[:-1])
    #print("\n".join(plain_lyrics[:-1]))