from gi.repository import Gtk

@Gtk.Template(resource_path="/com/github/dzheremi/lrcmake/gtk/components/noDirSelectedGreeting.ui")
class noDirSelectedGreeting(Gtk.Box):
    __gtype_name__ = 'noDirSelectedGreeting'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
