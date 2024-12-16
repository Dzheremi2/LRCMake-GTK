import os

from gi.repository import Gtk, GLib, Gdk # type: ignore

from .fileDetails import fileDetails
from lrcmake import shared

@Gtk.Template(resource_path=shared.PREFIX + "/gtk/components/songCard.ui")
class songCard(Gtk.Box):
    __gtype_name__ = 'songCard'

    cover: Gtk.Image = Gtk.Template.Child()
    song_title: Gtk.Inscription = Gtk.Template.Child()
    song_artist: Gtk.Inscription = Gtk.Template.Child()
    play_button: Gtk.Button = Gtk.Template.Child()
    edit_button: Gtk.Button = Gtk.Template.Child()
    card_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()

    def __init__(self, track_title = "Unknown", track_artist = "Unknown", track_cover = None, track_path = None, filename = None):
        super().__init__()
        self.song_cover = track_cover
        self.artist = track_artist
        self.title = track_title
        self.filename = filename
        self.path = track_path
        self.event_controller_motion = Gtk.EventControllerMotion.new()
        self.add_controller(self.event_controller_motion)
        self.event_controller_motion.connect('enter', self.toggle_buttons)
        self.event_controller_motion.connect('leave', self.toggle_buttons, None, None)
        self.song_title.set_property('text', track_title)
        self.song_artist.set_property('text', track_artist)
        self.click_gesture = Gtk.GestureClick(button = 1)
        self.click_gesture.connect('pressed', self.button_clicked)
        self.play_button.connect('clicked', self.button_clicked)
        self.cover.add_controller(self.click_gesture)
        if self.song_cover != None:
            if type(self.song_cover) == str:
                self.cover.set_from_file(self.song_cover)
            else:
                image_bytes = GLib.Bytes(track_cover)
                image_texture = Gdk.Texture.new_from_bytes(image_bytes)
                self.cover.props.paintable = image_texture

    def toggle_buttons(self, *args):
        if self.card_buttons_revealer.get_reveal_child() == False:
            self.card_buttons_revealer.set_reveal_child(True)
        else:   
            self.card_buttons_revealer.set_reveal_child(False)

    def button_clicked(self, *args):
        from lrcmake.methods.parsers import file_parser
        shared.win.title = self.title
        shared.win.artist = self.artist
        shared.win.filename = self.filename
        shared.win.filepath = self.path
        shared.win.sync_page_title.set_text(self.title)
        shared.win.sync_page_artist.set_text(self.artist)
        shared.win.controls.set_media_stream(Gtk.MediaFile.new_for_filename(self.path))
        if self.song_cover != None:
            shared.win.sync_page_cover.set_from_paintable(self.cover.props.paintable)
        else:
            shared.win.sync_page_cover.set_from_icon_name("note-placeholder")
        if (self.filename[:-4] + shared.schema.get_string("auto-file-format") in os.listdir(shared.state_schema.get_string("opened-dir-path"))) and (shared.schema.get_boolean("auto-file-manipulation") == True):
            file_parser(shared.state_schema.get_string("opened-dir-path") + "/" + self.filename[:-4] + shared.schema.get_string("auto-file-format"))
        shared.win.search_bar.set_search_mode(False)
        shared.win.nav_view.push(shared.win.syncing)

    def rmb_clicked(self, *args):
        dialog = fileDetails(title = self.title, artist = self.artist, filename = self.filename)
        dialog.present(shared.win)

    def get_title(self):
        return self.title
    
    def get_artist(self):
        return self.artist
    
    def get_path(self):
        return self.path
    
    def get_filename(self):
        return self.filename