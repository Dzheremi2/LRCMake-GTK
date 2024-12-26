from typing import Union

from gi.repository import GObject, Gtk  # type: ignore

from chronograph import shared
from chronograph.ui.BoxDialog import BoxDialog
from chronograph.utils.file_mutagen_id3 import FileID3
from chronograph.utils.file_mutagen_vorbis import FileVorbis

label_str = _("About File")
title_str = _("Title")
artist_str = _("Artist")
album_str = _("Album")
path_str = _("Path")


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/SongCard.ui")
class SongCard(Gtk.Box):
    """Card with Title, Artist and Cover of provided file

    Parameters
    # ----------
    file : Union[FileID3, FileVorbis]
        File of `.ogg`, `.flac`, `.mp3` and `.wav` formats

    GTK Objects
    ----------
    ::

        buttons_revealer: Gtk.Revealer -> Revealer for Play and Edit buttons
        play_button: Gtk.Button -> Play button
        metadata_editor_button: Gtk.Button -> Metadata editor button
        info_button: Gtk.Button -> File info button
        cover_button: Gtk.Button -> Clickable cover of song
        cover: Gtk.Image -> Cover image of song
        title_label: Gtk.Label -> Title of song
        artist_label: Gtk.Label -> Artist of song
    """

    __gtype_name__ = "SongCard"

    buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    play_button: Gtk.Button = Gtk.Template.Child()
    metadata_editor_button: Gtk.Button = Gtk.Template.Child()
    info_button: Gtk.Button = Gtk.Template.Child()
    cover_button: Gtk.Button = Gtk.Template.Child()
    cover_img: Gtk.Image = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()
    artist_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, file: Union[FileID3, FileVorbis]) -> None:
        super().__init__()
        self._file: Union[FileID3, FileVorbis] = file
        self.title_label.set_text(self._file.title)
        self.artist_label.set_text(self._file.artist)
        self.event_controller_motion = Gtk.EventControllerMotion.new()
        self.add_controller(self.event_controller_motion)
        self.event_controller_motion.connect("enter", self.toggle_buttons)
        self.event_controller_motion.connect("leave", self.toggle_buttons)
        self.info_button.connect(
            "clicked",
            lambda *_: BoxDialog(
                label_str,
                (
                    (title_str, self.title),
                    (artist_str, self.artist),
                    (album_str, self.album),
                    (path_str, self._file.path),
                ),
            ).present(shared.win),
        )
        self.cover_button.connect("clicked", self.on_play_button_clicked)
        self.play_button.connect("clicked", self.on_play_button_clicked)
        self.metadata_editor_button.connect(
            "clicked",
            lambda *_: self.set_property(
                "cover", open("/home/dzheremi/Pictures/pp.jpg", "rb").read()
            ),
        )
        self.bind_props()
        self.invalidate_cover(self.cover_img)

    def toggle_buttons(self, *_args) -> None:
        """Sets if buttons should be visible or not"""
        self.buttons_revealer.set_reveal_child(
            not self.buttons_revealer.get_reveal_child()
        )

    def invalidate_update(self, property: str, scope: str = "self") -> None:
        """Automatically updates interface labels on property change

        Parameters
        ----------
        property : str
            name of propety in `chronograph.utils.file.BaseFile` which triggers update
        scope : str, optional
            scope of update, by default "self", may be "sync_page"
        """
        if scope == "self":
            getattr(self, f"{property}_label").set_text(getattr(self, f"{property}"))
        elif scope == "sync_page":
            getattr(shared.win, f"sync_page_{property}").set_text(
                getattr(self, f"{property}")
            )

    def invalidate_cover(self, widget: Gtk.Image) -> None:
        """Automatically updates cover on property change"""
        if (_texture := self._file.get_cover_texture()) == "icon":
            widget.set_from_icon_name("note-placeholder")
        else:
            widget.props.paintable = _texture

    def bind_props(self) -> None:
        """Binds properties to update interface labels on change"""
        self.connect(
            "notify::title",
            lambda _object, property: self.invalidate_update(property.name),
        )
        self.connect(
            "notify::artist",
            lambda _object, property: self.invalidate_update(property.name),
        )
        self.connect("notify::cover", lambda *_: self.invalidate_cover(self.cover_img))

    def on_play_button_clicked(self, *_args) -> None:
        """Opens sync page for `self` and media stream"""
        shared.win.loaded_card = self
        self.invalidate_cover(shared.win.sync_page_cover)
        self.invalidate_update("title", "sync_page")
        self.invalidate_update("artist", "sync_page")
        mediastream = Gtk.MediaFile.new_for_filename(self._file.path)
        shared.win.controls.set_media_stream(mediastream)
        shared.win.controls_shrinked.set_media_stream(mediastream)
        shared.win.navigation_view.push(shared.win.sync_navigation_page)

    @GObject.Property(type=str)
    def title(self) -> str:
        return self._file.title

    @title.setter
    def title(self, value: str) -> None:
        self._file.title = value

    @GObject.Property(type=str)
    def artist(self) -> str:
        return self._file.artist

    @artist.setter
    def artist(self, value: str) -> None:
        self._file.artist = value

    @GObject.Property(type=str)
    def album(self) -> str:
        return self._file.album

    @album.setter
    def album(self, value: str) -> None:
        self._file.album = value

    @GObject.Property
    def cover(self) -> Union[str, bytes]:
        return self._file.cover

    @cover.setter
    def cover(self, data: bytes) -> None:
        if type(data) == bytes:
            self._file.cover = data
        else:
            raise ValueError("Cover must be bytes")
