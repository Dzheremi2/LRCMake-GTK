from gi.repository import Gdk, GLib, Gtk

import os
import eyed3
import magic
import re

from lrcmake.components.songCard import songCard
from lrcmake import shared

# Parsing directory for media files and adding cards to Library
def dir_parser(path, *args):
    shared.win.source_selection_button.set_child(Gtk.Spinner(spinning=True))
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
    shared.win.sort_revealer.set_reveal_child(shared.win.sorting_menu)
    shared.win.source_selection_button.set_icon_name("dir-open-symbolic")
    shared.state_schema.set_string("opened-dir-path", path)
    print(shared.state_schema.get_string("opened-dir-path"))

# Sorts cards using title from "a-z" or "z-a"
def sorting(child1, child2):
    order = None
    if shared.win.sort_state == "a-z":
        order = False
    elif shared.win.sort_state == "z-a":
        order = True
    return ((child1.get_child().get_title() > child2.get_child().get_title()) ^ order) * 2 - 1

def filtering(child):
    try:
        card = child.get_child()
        text = shared.win.search_entry.get_text().lower()
        filtered = text != "" and not (text in card.get_title().lower() or text in card.get_artist().lower())
        return not filtered
    except AttributeError:
        pass

# Parsing selected file for oneshot file syncing
def song_file_parser(path):
    audiofile = eyed3.load(path)
    try:
        title = audiofile.tag.title if audiofile.tag.title != None else "Unknown"
        artist = audiofile.tag.artist if audiofile.tag.artist != None else "Unknown"
        cover = audiofile.tag.images[0].image_data if  audiofile.tag.images[0].image_data != None else None
    except AttributeError:
        title = "Unknown"
        artist = "Unknown"
        cover = None
    shared.win.title = title
    shared.win.artist = artist
    shared.win.filepath = path
    shared.win.filename = os.path.basename(path)
    shared.win.sync_page_title.set_text(title)
    shared.win.sync_page_artist.set_text(artist)
    if cover != None:
        image_bytes = GLib.Bytes(cover)
        image_texture = Gdk.Texture.new_from_bytes(image_bytes)
        shared.win.sync_page_cover.props.paintable = image_texture
    else:
        shared.win.sync_page_cover.set_from_icon_name("note-placeholder")
    shared.win.controls.set_media_stream(Gtk.MediaFile.new_for_filename(path))
    shared.win.nav_view.push(shared.win.syncing)

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
    from lrcmake.components.syncLine import syncLine
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
    from lrcmake.components.syncLine import syncLine
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
