from gi.repository import Gtk
from lrcmake import shared

@Gtk.Template(resource_path=shared.PREFIX + "/gtk/components/noDirSelectedGreeting.ui")
class noDirSelectedGreeting(Gtk.Box):
    __gtype_name__ = 'noDirSelectedGreeting'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
