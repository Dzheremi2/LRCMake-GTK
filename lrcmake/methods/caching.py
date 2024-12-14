import yaml
import os
import eyed3
from gi.repository import GLib, Gdk, Adw # type: ignore
from lrcmake import shared

def save_location():
    shared.cache_file = open(str(shared.data_dir) + "/cache.yaml", "r+", encoding='utf-8')
    shared.cache = yaml.safe_load(shared.cache_file)
    if len(shared.cache['pins']) == 0:
        print("Triggered len method")
        entry = {
            "path": shared.state_schema.get_string("opened-dir-path"),
            "name": os.path.basename(shared.state_schema.get_string("opened-dir-path")),
            "isCached": shared.schema.get_boolean("cache-songs"),
            "cache": None
        }

        if shared.schema.get_boolean("cache-songs"):
            entry["cache"] = save_cache()

        shared.cache['pins'].append(entry)
        shared.cache_file.seek(0)
        yaml.dump(shared.cache, shared.cache_file, sort_keys=False, encoding=None, allow_unicode=True)
        shared.win.build_sidebar_content()
        shared.cache = yaml.safe_load(shared.cache_file)
    else:
        entries = []
        for entry in shared.cache['pins']:
            entries.append(entry['path'])
        if not shared.state_schema.get_string("opened-dir-path") in entries:
            print("Triggered multiple method")
            entry = {
                "path": shared.state_schema.get_string("opened-dir-path"),
                "name": os.path.basename(shared.state_schema.get_string("opened-dir-path")),
                "isCached": shared.schema.get_boolean("cache-songs"),
                "cache": None
            }

            if shared.schema.get_boolean("cache-songs"):
                entry["cache"] = save_cache()

            shared.cache['pins'].append(entry)
            shared.cache_file.seek(0)
            yaml.dump(shared.cache, shared.cache_file, sort_keys=False, encoding=None, allow_unicode=True)
            shared.win.lib_toast_overlay.add_toast(Adw.Toast(title = _("Direcotry saved successfully"))) # type: ignore
            shared.win.build_sidebar_content()
            shared.cache = yaml.safe_load(shared.cache_file)
        shared.win.lib_toast_overlay.add_toast(Adw.Toast(title = _("This folder is already in saves"))) # type: ignore

def save_cache():
    cache = []

    if not shared.state_schema.get_string("opened-dir-path").replace("/", ".")[1:] in os.listdir(str(shared.data_dir) + "/covers"):
        os.mkdir(f"{str(shared.data_dir)}/covers/{shared.state_schema.get_string("opened-dir-path").replace("/", ".")[1:]}")

    for item in shared.win.music_lib:
        card = item.get_child()
        if (shared.schema.get_boolean("cache-covers") and card.song_cover != None):
            image_bytes = GLib.Bytes(card.song_cover)
            image_texture = Gdk.Texture.new_from_bytes(image_bytes)
            image_texture.save_to_png(f"{str(shared.data_dir)}/covers/{shared.state_schema.get_string("opened-dir-path").replace("/", ".")[1:]}/{card.get_filename()[:-4]}.png")
            cover_path = f"{str(shared.data_dir)}/covers/{shared.state_schema.get_string("opened-dir-path").replace("/", ".")[1:]}/{card.get_filename()[:-4]}.png"
        else:
            cover_path = None

        album = "Unknown"
        if not card.get_path().endswith(".ogg"):
            if eyed3.load(card.get_path()) != None:
                if eyed3.load(card.get_path()).tag != None:
                    if eyed3.load(card.get_path()).tag.artist != None:
                        album = eyed3.load(card.get_path()).tag.album

        file = {
            "path": card.get_path(),
            "filename": card.get_filename(),
            "title": card.get_title(),
            "artist": card.get_artist(),
            "album": album,
            "cover_path": cover_path,
        }
        cache.append(file)
    return cache