import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

# pylint: disable=wrong-import-position
from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # type: ignore

from chronograph import shared
from chronograph.window import ChronographWindow


class ChronographApplication(Adw.Application):
    """Application class"""

    win: ChronographWindow

    def __init__(self) -> None:
        super().__init__(
            application_id=shared.APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_resource_path(shared.PREFIX + "/data/icons")

    def do_activate(self) -> None:  # pylint: disable=arguments-differ
        """Emits on app creation"""

        win = self.props.active_window  # pylint: disable=no-member
        if not win:
            shared.win = win = ChronographWindow(application=self)

        self.create_actions(
            {
                ("quit", ("<primary>q",)),
                ("toggle_sidebar", ("F9",), shared.win),
                ("toggle_search", ("<primary>f",), shared.win),
                ("select_dir", ("<primary><shift>o",), shared.win),
                ("append_line", ("<Alt>a",), shared.win),
                ("remove_selected_line", ("<Alt>r",), shared.win)
            }
        )

        sorting_action = Gio.SimpleAction.new_stateful(
            "sort_type",
            GLib.VariantType.new("s"),
            sorting_mode := GLib.Variant(
                "s", shared.state_schema.get_string("sorting")
            ),
        )
        sorting_action.connect("activate", shared.win.on_sorting_type_action)
        self.add_action(sorting_action)

        shared.win.present()

    def on_quit_action(self, *_args) -> None:
        self.quit()

    def create_actions(self, actions: set) -> None:
        """Creates actions for provided scope with provided accels

        Args:
            actions (set): Actions in format ("name", ("accels",), scope)

            accels, scope: optional
        """
        for action in actions:
            simple_action = Gio.SimpleAction.new(action[0], None)

            scope = action[2] if action[2:3] else self
            simple_action.connect("activate", getattr(scope, f"on_{action[0]}_action"))

            if action[1:2]:
                self.set_accels_for_action(
                    f"app.{action[0]}" if scope == self else f"win.{action[0]}",
                    action[1],
                )
            scope.add_action(simple_action)


def main(_version):
    """App entrypoint"""
    shared.app = app = ChronographApplication()
    return app.run(sys.argv)
