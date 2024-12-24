from .file import BaseFile

class FileVorbis(BaseFile):
    """A Vorbis (ogg, flac) compatible file class. Inherited from `BaseFile`

    Parameters
    --------
    path : str
        A path to file for loading
    """

    def load_cover(self) -> None: ...
    def load_str_data(self, tags: list = ["title", "artist", "album"]) -> None: ...
