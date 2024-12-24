from typing import Union

from gi.repository import Gdk

class BaseFile:
    """A base class for mutagen filetypes classes

    Parameters
    ----------
    path : str
        A path to file for loading

    Props
    --------
    ::

        title : str -> Title of song
        artist : str -> Artist of song
        album : str -> Album of song
        cover : Gdk.Texture | str -> Cover of song
    """

    _title: str
    _artist: str
    _album: str
    _cover: Union[bytes, str]
    _mutagen_file: dict

    _path: str

    def load_from_file(self, path: str) -> None: ...
    def get_cover_texture(self) -> Union[Gdk.Texture, str]: ...
    def load_str_data(self) -> None: ...
    def load_cover(self) -> None: ...
