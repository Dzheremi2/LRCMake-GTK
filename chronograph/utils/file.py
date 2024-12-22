from typing import Union

import mutagen
from gi.repository import Gdk, GLib  # type: ignore


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

    __gtype_name__ = "BaseFile"

    _title: str = "Unknown"
    _artist: str = "Unknown"
    _album: str = "Unknown"
    _cover: Union[Gdk.Texture, str] = None
    _mutagen_file: dict = None

    def __init__(self, path: str) -> None:
        self._path: str = path
        self.load_from_file(path)

    def load_from_file(self, path: str) -> None:
        """Generates mutagen file instance for path

        Parameters
        ----------
        path : str
            /path/to/file
        """
        self._mutagen_file = mutagen.File(path)

    def get_cover_texture(self) -> Union[Gdk.Texture, str]:
        """Prepares a Gdk.Texture for setting to SongCard.paintable

        Returns
        -------
        Union[Gdk.Texture, str]
            Gdk.Texture or 'icon' string if no cover
        """
        if not self._cover == "icon":
            _bytes = GLib.Bytes(self._cover)
            _texture = Gdk.Texture.new_from_bytes(_bytes)
            return _texture
        else:
            return "icon"

    @property
    def title(self) -> str:
        """Song title as str

        Returns
        -------
        str
            song title
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set song title with str

        Parameters
        ----------
        value : str
            new song title
        """
        self._title = value

    @property
    def artist(self) -> str:
        """Song  artist as str

        Returns
        -------
        str
            song artist
        """
        return self._artist

    @artist.setter
    def artist(self, value: str) -> None:
        """Set song artist as str

        Parameters
        ----------
        value : str
            new song artist
        """
        self._artist = value

    @property
    def album(self) -> str:
        """Song album as str

        Returns
        -------
        str
            song album
        """
        return self._album

    @album.setter
    def album(self, value: str) -> None:
        """Set song album as str

        Parameters
        ----------
        value : str
            new song album str
        """
        self._album = value

    @property
    def cover(self) -> bytes:
        """Song cover as bytes

        Returns
        -------
        bytes
            song cover
        """
        return self._cover

    @cover.setter
    def cover(self, data: bytes) -> None:
        """Set song cover image with bytes

        Parameters
        ----------
        data : bytes
            new song cover
        """
        self._cover = data

    def load_str_data(self) -> None:
        """Should be implemenmted in file specific child classes"""
        raise NotImplementedError

    def load_cover(self) -> None:
        """Should be implemenmted in file specific child classes"""
        raise NotImplementedError
