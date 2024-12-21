import os

from .file import BaseFile


class FileID3(BaseFile):
    __gtype_name__ = "FileID3"

    def __init__(self, path):
        super().__init__(path)
        self.load_cover()
        self.load_str_data()

    # pylint: disable=attribute-defined-outside-init
    def load_cover(self) -> None:
        """Extracts cover from song file. If no cover, then sets cover as 'icon'"""
        pictures = self._mutagen_file.tags.getall("APIC")
        if len(pictures) != 0:
            self._cover = pictures[0].data
        if len(pictures) == 0:
            self._cover = "icon"

    def load_str_data(self) -> None:
        """Sets all string data from tags. If data is unavailable, then sets 'Unknown'
        """
        if (_title := self._mutagen_file.tags["TIT2"].text[0]) is not None:
            self._title = _title
        else:
            self._title = os.path.basename(self._path)

        if (_artist := self._mutagen_file.tags["TPE1"].text[0]) is not None:
            self._artist = _artist
        else:
            self._artist = "Unknown"

        if (_album := self._mutagen_file.tags["TALB"].text[0]) is not None:
            self._album = _album
        else:
            self._album = "Unknown"
