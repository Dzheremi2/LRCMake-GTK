from typing import Union

from chronograph.utils.file_mutagen_id3 import FileID3
from chronograph.utils.file_mutagen_vorbis import FileVorbis

def dir_parser(path: str, *_args) -> None: ...
def songcard_idle(file: Union[FileID3, FileVorbis]) -> None: ...
