from .file import BaseFile

class FileID3(BaseFile):
    """A ID3 compatible file class. Inherited from `BaseFile`

    Parameters
    --------
    path : str
        A path to file for loading
    """

    def load_cover(self) -> None: ...
    def load_str_data(self) -> None: ...
