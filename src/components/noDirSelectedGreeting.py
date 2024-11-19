from gi.repository import Gtk

@Gtk.Template(resource_path="/io/github/dzheremi2/lrcmake_gtk/gtk/components/noDirSelectedGreeting.ui")
class noDirSelectedGreeting(Gtk.Box):
    __gtype_name__ = 'noDirSelectedGreeting'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
