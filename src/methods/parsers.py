from gi.repository import Gdk

import os
import eyed3
import magic
import re

from .songCard import songCard
from .selectData import select_lyrics_file
from .syncLine import syncLine
from . import shared

# Parsing directory for media files and adding cards to Library
def dir_parser(path, *args):
    from . import main
    shared.win.music_lib.remove_all()
    shared.win.music_lib.set_property('halign', 'start')
    shared.win.music_lib.set_property('valign', 'start')
    shared.win.music_lib.set_property('homogeneous', True)
    for file in os.listdir(path + "/"):
        if not os.path.isdir(path + "/" + file):
            mime_type = magic.from_file(path + "/" + file, mime = True)
            if mime_type.startswith('audio/'):
                audiofile = eyed3.load(path + "/" + file)
                try:
                    if audiofile.tag.images[0].image_data != None and audiofile.tag.title != None and audiofile.tag.artist != None:
                        image_bytes = audiofile.tag.images[0].image_data
                        shared.win.music_lib.append(songCard(
                            track_title = audiofile.tag.title,
                            track_artist = audiofile.tag.artist,
                            track_cover = image_bytes,
                            track_path = path + "/" + file,
                            filename = file
                            )
                        )
                except AttributeError:
                    shared.win.music_lib.append(songCard(track_title = file, filename = file, track_path = path + "/" + file))

# Parse focused line for timestamp
def line_parser():
    pattern = r'\[([^\[\]]+)\]'
    return re.search(pattern, shared.selected_row.get_text())[0]

# Parse focused line for getting it's timestamp in ms
def timing_parser():
    pattern = r"(\d+):(\d+).(\d+)"
    mm, ss, ms = re.search(pattern, line_parser()).groups()
    total_ss = int(mm) * 60 + int(ss)
    total_ms = total_ss * 1000 + int(ms)
    return total_ms

# Parse focused line for timestamp with argument
def arg_line_parser(string):
    pattern = r'\[([^\[\]]+)\]'
    try:
        return re.search(pattern, string)[0]
    except TypeError:
        return None

# Parse focused line for getting it's timestamp in ms with argument
def arg_timing_parser(string):
    try:
        pattern = r"(\d+):(\d+).(\d+)"
        mm, ss, ms = re.search(pattern, arg_line_parser(string)).groups()
        total_ss = int(mm) * 60 + int(ss)
        total_ms = total_ss * 1000 + int(ms)
        return total_ms
    except TypeError:
        return None

# Getting user's clipbord
def clipboard_parser(*args):
    clipboard = Gdk.Display().get_default().get_clipboard()
    clipboard.read_text_async(None, on_clipboard_parsed, user_data=clipboard)

# Sets lines with text from clipboard
def on_clipboard_parsed(_clipboard, result, clipboard):
    from . import main
    data = clipboard.read_text_finish(result)
    list = data.splitlines()
    shared.lyrics_list = list
    childs = []
    for child in shared.win.lyrics_lines_box:
        childs.append(child)
    shared.win.lyrics_lines_box.remove_all()
    for i in range(len(list)):
        shared.win.lyrics_lines_box.append(syncLine())
        shared.win.lyrics_lines_box.get_row_at_index(i).set_text(list[i])

# Parse file for for setting it's content to lines box
def file_parser(path):
    from . import shared
    file = open(path, 'r')
    list = file.read().splitlines()
    shared.lyrics_list = list
    childs = []
    for child in shared.win.lyrics_lines_box:
        childs.append(child)
    shared.win.lyrics_lines_box.remove_all()
    for i in range(len(list)):
        shared.win.lyrics_lines_box.append(syncLine())
        shared.win.lyrics_lines_box.get_row_at_index(i).set_text(list[i])
