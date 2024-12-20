from typing import Union

from gi.repository import Gtk  # type: ignore

from chronograph import shared
from chronograph.utils.file_mutagen_id3 import FileID3


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/SongCard.ui")
class SongCard(Gtk.Box):
    __gtype_name__ = "SongCard"

    buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    play_button: Gtk.Button = Gtk.Template.Child()
    metadata_editor_button: Gtk.Button = Gtk.Template.Child()
    cover_button: Gtk.Button = Gtk.Template.Child()
    cover: Gtk.Image = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()
    artist_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, file: Union[FileID3]):
        super().__init__()
        self._file = file
        self.title_label.set_text(self._file._title)
        self.artist_label.set_text(self._file._artist)
        self.event_controller_motion = Gtk.EventControllerMotion.new()
        self.add_controller(self.event_controller_motion)
        self.event_controller_motion.connect("enter", self.toggle_buttons)
        self.event_controller_motion.connect("leave", self.toggle_buttons, None, None)

        if (_texture := self._file.get_cover_texture()) == "icon":
            self.cover.set_from_icon_name("note-placeholder")
        else:
            self.cover.props.paintable = _texture

    def toggle_buttons(self, *_args) -> None:
        self.buttons_revealer.set_reveal_child(
            not self.buttons_revealer.get_reveal_child()
        )
