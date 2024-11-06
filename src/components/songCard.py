from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk


@Gtk.Template(resource_path="/com/github/dzheremi/lrcmake/gtk/components/songCard.ui")
class songCard(Gtk.Box):
    __gtype_name__ = 'songCard'

    cover = Gtk.Template.Child()
    song_title = Gtk.Template.Child()
    song_artist = Gtk.Template.Child()

    def __init__(self, track_title = _("Unknown"), track_artist = _("Unknown"), track_cover = None, track_path = None):
        super().__init__()
        self.cover.set_filename('/home/dzheremi/Pictures/note.png')
        self.song_title.set_property('label', track_title)
        self.song_artist.set_property('label', track_artist)
        if track_cover != None:
            image_bytes = GLib.Bytes(track_cover)
            image_texture = Gdk.Texture.new_from_bytes(image_bytes)
            self.cover.props.paintable = image_texture
