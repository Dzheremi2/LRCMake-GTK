import os

from .file import BaseFile


class FileID3(BaseFile):
    """A ID3 compatible file class. Inherited from `BaseFile`

    Parameters
    --------
    path : str
        A path to file for loading
    """

    __gtype_name__ = "FileID3"

    def __init__(self, path) -> None:
        super().__init__(path)
        self.load_cover()
        self.load_str_data()

    # pylint: disable=attribute-defined-outside-init
    def load_cover(self) -> None:
        """Extracts cover from song file. If no cover, then sets cover as `icon`"""
        if self._mutagen_file.tags is not None:
            pictures = self._mutagen_file.tags.getall("APIC")
            if len(pictures) != 0:
                self._cover = pictures[0].data
            if len(pictures) == 0:
                self._cover = "icon"
        else:
            self._cover = "icon"

    def load_str_data(self) -> None:
        """Sets all string data from tags. If data is unavailable, then sets `Unknown`"""
        if self._mutagen_file.tags is not None:
            if (_title := self._mutagen_file.tags["TIT2"].text[0]) is not None:
                self._title = _title

            if (_artist := self._mutagen_file.tags["TPE1"].text[0]) is not None:
                self._artist = _artist

            if (_album := self._mutagen_file.tags["TALB"].text[0]) is not None:
                self._album = _album
        else:
            self._title = os.path.basename(self._path)
