from gi.repository import Adw, Gtk  # type: ignore

from chronograph import shared


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class ChronographWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "ChronographWindow"

    overlay_split_view: Adw.OverlaySplitView = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def on_toggle_sidebar_action(self, *_args) -> None:
        value = not self.overlay_split_view.get_show_sidebar()
        self.overlay_split_view.set_show_sidebar(value)
