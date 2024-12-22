import base64
import os

from mutagen.flac import FLAC, Picture
from mutagen.flac import error as FLACError

from .file import BaseFile


class FileVorbis(BaseFile):
    """A Vorbis (ogg, flac) compatible file class. Inherited from `BaseFile`

    Parameters
    --------
    path : str
        A path to file for loading
    """

    __gtype_name__ = "FileVorbis"

    def __init__(self, path) -> None:
        super().__init__(path)

        self.load_cover()
        self.load_str_data()

    def load_cover(self) -> None:
        """Loads cover for Vorbis format audio"""
        if isinstance(self._mutagen_file, FLAC) and self._mutagen_file.pictures:
            if self._mutagen_file.pictures[0].data is not None:
                self._cover = self._mutagen_file.pictures[0].data
            else:
                self._cover = "icon"
            print("FLAC")
        elif self._mutagen_file.get("metadata_block_picture", []):
            _data = None
            for base64_data in self._mutagen_file.get("metadata_block_picture", []):
                try:
                    _data = base64.b64decode(base64_data)
                except (TypeError, ValueError):
                    continue

                try:
                    _data = Picture(_data).data
                except FLACError:
                    continue

            if _data is None:
                self._cover = "icon"
            else:
                self._cover = _data
        else:
            self._cover = "icon"

    def load_str_data(self, tags: list = ["title", "artist", "album"]) -> None:
        """Loads title, artist and album for Vorbis media format

        Parameters
        ----------
        tags : list, persistent
            list of tags for parsing in vorbis comment, by default `["title", "artist", "album"]`
        """
        if self._mutagen_file.tags is not None:
            for tag in tags:
                try:
                    text = (
                        "Unknown"
                        if not self._mutagen_file.tags[tag.lower()][0]
                        else self._mutagen_file.tags[tag.lower()][0]
                    )
                    setattr(self, f"_{tag}", text)
                except KeyError:
                    try:
                        text = (
                            "Unknown"
                            if not self._mutagen_file.tags[tag.upper()][0]
                            else self._mutagen_file.tags[tag.upper()][0]
                        )
                        setattr(self, f"_{tag}", text)
                    except KeyError:
                        setattr(self, f"_{tag}", "Unknown")
        if self._title == "Unknown":
            self._title = os.path.basename(self._path)
