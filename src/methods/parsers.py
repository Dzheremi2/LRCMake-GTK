from gi.repository import Gtk

import os
import eyed3
import sys
import magic
import io

from .songCard import songCard

def dir_parser(path):
    from . import main
    main.app.win.music_lib.remove_all()
    main.app.win.music_lib.set_property('halign', 'start')
    main.app.win.music_lib.set_property('valign', 'start')
    main.app.win.music_lib.set_property('homogeneous', True)
    for file in os.listdir(path + "/"):
        if not os.path.isdir(path + "/" + file):
            mime_type = magic.from_file(path + "/" + file, mime = True)
            if mime_type.startswith('audio/'):
                audiofile = eyed3.load(path + "/" + file)
                try:
                    if audiofile.tag.images[0].image_data != None and audiofile.tag.title != None and audiofile.tag.artist != None:
                        image_bytes = audiofile.tag.images[0].image_data
                        main.app.win.music_lib.append(songCard(track_title = audiofile.tag.title, track_artist = audiofile.tag.artist, track_cover = image_bytes, track_path = path + "/" + file, filename = file))
                except AttributeError:
                    main.app.win.music_lib.append(songCard(track_title = file, filename = file))
