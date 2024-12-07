from gi.repository import Gtk, Adw  # type: ignore


@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake-gtk/gtk/components/lrclibWindow.ui")
class lrclibWindow(Adw.Dialog):
    __gtype_name__ = "lrclibWindow"

    title_entry = Gtk.Template.Child()
    artist_entry = Gtk.Template.Child()
    results_list = Gtk.Template.Child()
    synced_lyrics_text_view = Gtk.Template.Child()
    plain_lyrics_text_view = Gtk.Template.Child()
    copy_button = Gtk.Template.Child()

    opened = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__class__.opened = True
        self.connect("closed", lambda _: self.set_opened(False))

    def set_opened(self, opened):
        self.__class__.opened = opened
    	