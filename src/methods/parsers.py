from gi.repository import Gtk

import os
import eyed3
import sys
import magic
from PIL import Image
import io

from .songCard import songCard

def dir_parser(path):
    from . import main
    for file in os.listdir(path + "/"):
        if not os.path.isdir(path + "/" + file):
            mime_type = magic.from_file(path + "/" + file, mime = True)
            if mime_type.startswith('audio/'):
                audiofile = eyed3.load(path + "/" + file)
                try:
                    if audiofile.tag.images[0].image_data != None and audiofile.tag.title != None and audiofile.tag.artist != None:
                        image = Image.open(io.BytesIO(audiofile.tag.images[0].image_data))
                        image = image.resize((160, 160))
                        image_bytes = io.BytesIO()
                        image.save(image_bytes, format="PNG")
                        main.app.win.music_lib.append(songCard(track_title = audiofile.tag.title, track_artist = audiofile.tag.artist, track_cover = image_bytes.getvalue(), track_path = path + "/" + file))
                except AttributeError:
                    main.app.win.music_lib.append(songCard())
