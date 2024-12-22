import threading
from typing import Any

from gi.repository import Gio, Gtk  # type: ignore

from chronograph import shared
from chronograph.utils.parsers import dir_parser


def select_dir(*_args) -> None:
    """Creates `Gtk.FileDialog` to select directory for parsing by `chronograph.utils.parsers.dir_parser`"""
    dialog = Gtk.FileDialog(
        default_filter=Gtk.FileFilter(mime_types=["inode/directory"])
    )
    dialog.select_folder(shared.win, None, on_selected_dir)


def on_selected_dir(file_dialog: Gtk.FileDialog, result: Gio.Task) -> None:
    """Callbacked by `select_dir`. Creates thread for `chronograph.utils.parsers.dir_parser` launches this function in it

    Parameters
    ----------
    file_dialog : Gtk.FileDialog
        FileDialog, callbacked from `select_dir`
    result : Gio.Task
        Task for reading, callbacked from `select_dir`
    """
    print(result)
    dir = file_dialog.select_folder_finish(result)
    thread = threading.Thread(target=lambda: (dir_parser(dir.get_path())))
    thread.daemon = True
    thread.start()
