from typing import Union

from gi.repository import Gtk  # type: ignore

from chronograph import shared
from chronograph.utils.file_mutagen_id3 import FileID3
from chronograph.utils.file_mutagen_vorbis import FileVorbis


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/SongCard.ui")
class SongCard(Gtk.Box):
    """Card with Title, Artist and Cover of provided file

    Parameters
    ----------
    file : Union[FileID3, FileVorbis]
        File of `.ogg`, `.flac`, `.mp3` and `.wav` formats

    GTK Objects
    ----------
    ::

        buttons_revealer: Gtk.Revealer -> Revealer for Play and Edit buttons
        play_button: Gtk.Button -> Play button
        metadata_editor_button: Gtk.Button -> Metadata editor button
        cover_button: Gtk.Button -> Clickable cover of song
        cover: Gtk.Image -> Cover image of song
        title_label: Gtk.Label -> Title of song
        artist_label: Gtk.Label -> Artist of song
    """

    __gtype_name__ = "SongCard"

    buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    play_button: Gtk.Button = Gtk.Template.Child()
    metadata_editor_button: Gtk.Button = Gtk.Template.Child()
    cover_button: Gtk.Button = Gtk.Template.Child()
    cover: Gtk.Image = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()
    artist_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, file: Union[FileID3, FileVorbis]) -> None:
        super().__init__()
        self._file: Union[FileID3, FileVorbis] = file
        self.title_label.set_text(self._file._title)
        self.artist_label.set_text(self._file._artist)
        self.event_controller_motion = Gtk.EventControllerMotion.new()
        self.add_controller(self.event_controller_motion)
        self.event_controller_motion.connect("enter", self.toggle_buttons)
        self.event_controller_motion.connect("leave", self.toggle_buttons)

        if (_texture := self._file.get_cover_texture()) == "icon":
            self.cover.set_from_icon_name("note-placeholder")
        else:
            self.cover.props.paintable = _texture

    def toggle_buttons(self, *_args) -> None:
        """Sets if buttons should be visible or not"""
        self.buttons_revealer.set_reveal_child(
            not self.buttons_revealer.get_reveal_child()
        )
