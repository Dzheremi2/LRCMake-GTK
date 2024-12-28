from typing import Union

from gi.repository import Gtk

from chronograph.utils.file_mutagen_id3 import FileID3
from chronograph.utils.file_mutagen_vorbis import FileVorbis  # type: ignore

label_str: str
title_str: str
artist_str: str
album_str: str
path_str: str

class SongCard(Gtk.Box):
    """Card with Title, Artist and Cover of provided file

    Parameters
    ----------
    file : Union[FileID3, FileVorbis]
        File of `.ogg`, `.flac`, `.mp3` and `.wav` formats
    """

    buttons_revealer: Gtk.Revealer
    play_button: Gtk.Button
    metadata_editor_button: Gtk.Button
    info_button: Gtk.Button
    cover_button: Gtk.Button
    cover_img: Gtk.Image
    title_label: Gtk.Label
    artist_label: Gtk.Label

    _file: Union[FileID3, FileVorbis]

    def toggle_buttons(self, *_args) -> None: ...
    def invalidate_update(self, property: str, scope: str = "self") -> None: ...
    def invalidate_cover(self, widget: Gtk.Image) -> None: ...
    def bind_props(self) -> None: ...
    def on_play_button_clicked(self, *_args) -> None: ...
