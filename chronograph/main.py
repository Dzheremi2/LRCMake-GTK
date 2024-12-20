import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

# pylint: disable=wrong-import-position
from gi.repository import Adw, Gdk, Gio, Gtk  # type: ignore

from chronograph import shared
from chronograph.window import ChronographWindow


class ChronographApplication(Adw.Application):
    win: ChronographWindow

    def __init__(self) -> None:
        super().__init__(application_id=shared.APP_ID)
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
            }
        )

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
