from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from .fileDetails import fileDetails
from . import main


@Gtk.Template(resource_path="/com/github/dzheremi/lrcmake/gtk/components/songCard.ui")
class songCard(Gtk.Box):
    __gtype_name__ = 'songCard'

    cover = Gtk.Template.Child()
    song_title = Gtk.Template.Child()
    song_artist = Gtk.Template.Child()
    cover_button = Gtk.Template.Child()

    def __init__(self, track_title = _("Unknown"), track_artist = _("Unknown"), track_cover = None, track_path = None, id = None, filename = None):
        super().__init__()
        self.song_cover = track_cover
        self.artist = track_artist
        self.title = track_title
        self.filename = filename
        self.cover_button.connect('clicked', self.button_clicked)
        self.cover.set_filename('/home/dzheremi/Pictures/note.png')
        self.song_title.set_property('text', track_title)
        self.song_artist.set_property('text', track_artist)
        self.click_gesture = Gtk.GestureClick(button = 3)
        self.click_gesture.connect("pressed", self.rmb_clicked)
        self.cover_button.add_controller(self.click_gesture)
        if track_cover != None:
            image_bytes = GLib.Bytes(track_cover)
            image_texture = Gdk.Texture.new_from_bytes(image_bytes)
            self.cover.props.paintable = image_texture

    def button_clicked(self):
        main.app.win.nav_view.push(main.app.win.syncing)

    def rmb_clicked(self, *args):
        dialog = fileDetails(title = str(self.title), artist = str(self.artist), filename = str(self.filename))
        dialog.present(main.app.win)
