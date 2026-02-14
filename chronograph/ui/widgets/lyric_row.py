from pathlib import Path

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from chronograph.backend.file import SongCardModel
from chronograph.backend.file.available_lyrics import TEXT_LABELS
from chronograph.backend.file.library_manager import LibraryManager
from chronograph.backend.lrclib.exceptions import APIRequestError
from chronograph.backend.lrclib.lrclib_service import LRClibService
from chronograph.backend.lyrics import (
  ChronieLyrics,
  ElrcLyrics,
  LrcLyrics,
  PlainLyrics,
  SrtLyrics,
  get_track_lyric,
)
from chronograph.internal import Constants
from chronograph.utils.launch import launch_path
from dgutils import Actions, Linker
from dgutils.typing import unwrap

logger = Constants.LOGGER


@Actions.from_schema(Constants.PREFIX + "/resources/actions/lyric_row_actions.yaml")
class LyricRow(Adw.ActionRow):
  __gtype_name__ = "LyricRow"

  def __init__(self, fmt: str, track_uuid: str, available: bool = True) -> None:
    super().__init__()
    self.track_uuid = track_uuid
    fmt_key = fmt.lower()
    self.set_title(TEXT_LABELS.get(fmt_key, fmt.upper()))

    # Setup prefix
    status_indicator = Gtk.Button(
      icon_name="chr-check-round-outline-symbolic", focusable=False
    )
    status_indicator.add_css_class("no-hover")
    status_indicator.add_css_class("flat")

    # Setup suffix
    box = Gtk.Box(valign=Gtk.Align.CENTER, spacing=4)
    export_menu = Gio.Menu()
    export_menu_section = Gio.Menu()
    if fmt_key == "lrc":
      export_menu_section.append("LRClib", "export.lrclib")
    export_file = Gio.MenuItem.new(_("File"))
    export_file.set_action_and_target_value(
      "export.file", GLib.Variant.new_string(fmt_key)
    )
    export_menu_section.append_item(export_file)
    export_clipboard = Gio.MenuItem.new(_("Clipboard"))
    export_clipboard.set_action_and_target_value(
      "export.clipboard", GLib.Variant.new_string(fmt_key)
    )
    export_menu_section.append_item(export_clipboard)
    export_menu.insert_section(0, _("Export To…"), export_menu_section)
    self.export_button = Gtk.MenuButton(
      menu_model=export_menu, icon_name="export-to-symbolic", css_classes=["flat"]
    )
    box.append(self.export_button)

    # Add prefix and suffix
    self.add_suffix(box)
    self.add_prefix(status_indicator)

    if available:
      status_indicator.add_css_class("success")
    else:
      status_indicator.add_css_class("warning")

  def _export_lrclib(self, *_args) -> None:
    chronie = unwrap(get_track_lyric(self.track_uuid))
    lrc = LrcLyrics.from_chronie(chronie)
    plain = PlainLyrics.from_chronie(chronie)
    if not lrc.is_finished():
      Constants.WIN.show_toast(_("Seems like not every line is synced"))
      return
    model = SongCardModel(LibraryManager.track_path(self.track_uuid), self.track_uuid)
    self.link = Linker()
    self.link.new_connection(LRClibService(), "publish-done", self._on_publish_done)
    self.link.new_connection(LRClibService(), "publish-failed", self._on_publish_failed)
    try:
      LRClibService().publish(model.media(), lrc.text, plain.text)
      self.export_button.set_child(Adw.Spinner())
      self.export_button.set_sensitive(False)
    except AttributeError:

      def reason(*_args) -> None:
        _alert = Adw.AlertDialog(
          heading=_("Unable to publish lyrics."),
          body=_(
            "To publish lyrics the track must have a title, artist, album and lyrics fields set."
          ),
          default_response="close",
          close_response="close",
        )
        _alert.add_response("close", _("Close"))
        _alert.present(Constants.WIN)

      Constants.WIN.show_toast(
        _("Cannot publish empty lyrics"),
        button_label=_("Why?"),
        button_callback=reason,
      )
      self.link.disconnect_all()
      self.export_button.set_sensitive(True)
      self.export_button.set_icon_name("export-to-symbolic")
      return

  def _on_publish_done(self, _service, status_code: int) -> None:
    if status_code == 201:
      Constants.WIN.show_toast(
        _("Published successfully: {code}").format(code=str(status_code)),
      )
    elif status_code == 400:
      Constants.WIN.show_toast(
        _("Incorrect publish token: {code}").format(code=str(status_code)),
      )
    else:
      Constants.WIN.show_toast(
        _("Unknown error occured: {code}").format(code=str(status_code)),
      )

    self.link.disconnect_all()
    self.export_button.set_sensitive(True)
    self.export_button.set_icon_name("export-to-symbolic")

  def _on_publish_failed(self, _service, error: Exception) -> None:
    log_path = Constants.CACHE_DIR / "chronograph" / "logs" / "chronograph.log"
    match error:
      case APIRequestError():
        Constants.WIN.show_toast(
          _("Network error occurred while publishing lyrics"),
          button_label=_("Log"),
          button_callback=lambda *__: launch_path(log_path),
        )
      case __:
        Constants.WIN.show_toast(
          _("An error occurred while publishing lyrics"),
          button_label=_("Log"),
          button_callback=lambda *__: launch_path(log_path),
        )
    self.link.disconnect_all()
    self.export_button.set_sensitive(True)
    self.export_button.set_icon_name("export-to-symbolic")

  def _export_file(self, _action, state: GLib.Variant) -> None:
    chronie = unwrap(get_track_lyric(self.track_uuid))
    model = SongCardModel(LibraryManager.track_path(self.track_uuid), self.track_uuid)

    # fmt: off
    match str(state).strip("'"):
      case "plain": ext = ".txt"
      case "lrc" | "elrc": ext = ".lrc"
      case "srt": ext = ".srt"
    # fmt: on

    format_filter = Gtk.FileFilter()
    format_filter.set_name(_("Lyrics ({pattern})").format(pattern=ext))
    format_filter.add_pattern(f"*{ext}")

    dialog = Gtk.FileDialog(
      initial_name=f"{model.title_display} - {model.artist_display}{ext}"
    )
    dialog.set_default_filter(format_filter)
    dialog.save(Constants.WIN, None, self._on_export_file_selected, chronie, state)

  def _on_export_file_selected(
    self,
    file_dialog: Gtk.FileDialog,
    result: Gio.Task,
    chronie: ChronieLyrics,
    state: GLib.Variant,
  ) -> None:
    filepath = unwrap(file_dialog.save_finish(result).get_path())
    suffix = Path(filepath).suffix.lower()
    if suffix == "":
      logger.warning("File must have a suffix for export")
      Constants.WIN.show_toast(_("File must have a suffix"))
      return
    # fmt: off
    match suffix:
        case ".txt": lyr_format = PlainLyrics
        case ".srt": lyr_format = SrtLyrics
        case ".lrc":
          lyr_format = ElrcLyrics if str(state).strip("'") == "elrc" else LrcLyrics
    # fmt: on
    text = lyr_format.from_chronie(chronie).to_file_text()
    Path(filepath).write_text(text, encoding="utf-8")
    logger.info("Lyrics exported to file: '%s'", filepath)

    Constants.WIN.show_toast(
      _("Lyrics exported to file"),
      button_label=_("Show"),
      button_callback=lambda *__: launch_path(Path(filepath)),
    )

  def _export_clipboard(self, _action, state: GLib.Variant) -> None:
    chronie = unwrap(get_track_lyric(self.track_uuid))
    # fmt: off
    match str(state).strip("'"):
        case "plain": lyr_format = PlainLyrics
        case "srt": lyr_format = SrtLyrics
        case "lrc": lyr_format = LrcLyrics
        case "elrc": lyr_format = ElrcLyrics
    # fmt: on
    clipboard = unwrap(Gdk.Display().get_default()).get_clipboard()
    clipboard.set(lyr_format.from_chronie(chronie).text)
    logger.info("Lyrics exported to clipboard")
    Constants.WIN.show_toast(_("Lyrics exported to clipboard"), timeout=3)
