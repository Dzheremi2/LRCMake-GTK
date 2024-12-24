import os
from pathlib import Path
from typing import Union

from gi.repository import GLib  # type: ignore

from chronograph import shared
from chronograph.ui.SongCard import SongCard
from chronograph.utils.file_mutagen_id3 import FileID3
from chronograph.utils.file_mutagen_vorbis import FileVorbis


def dir_parser(path: str, *_args) -> None:
    """Parses directory and creates `SongCard` instances for files in directory of formats `ogg`, `flac`, `mp3` and `wav`

    Parameters
    ----------
    path : str
        Path to directory to parse
    """
    shared.win.library.remove_all()
    shared.win.library_scrolled_window.set_child(shared.win.library)
    path = path + "/"
    mutagen_files = []
    for file in os.listdir(path):
        if not os.path.isdir(path + file):
            if Path(file).suffix in (".ogg", ".flac"):
                mutagen_files.append(FileVorbis(path + file))
            elif Path(file).suffix in (".mp3", ".wav"):
                mutagen_files.append(FileID3(path + file))

    for file in mutagen_files:
        GLib.idle_add(songcard_idle, file)

    shared.win.right_buttons_revealer.set_reveal_child(True)
    shared.win.left_buttons_revealer.set_reveal_child(True)
    # NOTE: This should be implemented in ALL parsers functions
    # for child in shared.win.library:
    #     child.set_focusable(False)


def songcard_idle(file: Union[FileID3, FileVorbis]) -> None:
    """Appends new `SongCard` instance to `ChronographWindow.library`

    Parameters
    ----------
    file : FileID3 | FileVorbis
        File of song
    """
    song_card = SongCard(file)
    shared.win.library.append(song_card)
    song_card.get_parent().set_focusable(False)
