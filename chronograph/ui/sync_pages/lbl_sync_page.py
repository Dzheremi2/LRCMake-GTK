"""Sync page for LRC format syncing"""

import re
import traceback
from pathlib import Path
from typing import Literal, Optional, cast

from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk, Pango

from chronograph.backend.converter import timestamp_to_ns
from chronograph.backend.file.song_card_model import SongCardModel
from chronograph.backend.file_parsers import parse_file
from chronograph.backend.lrclib.exceptions import APIRequestError
from chronograph.backend.lrclib.lrclib_service import LRClibService
from chronograph.backend.lyrics import (
  ChronieLyrics,
  LrcLyrics,
  PlainLyrics,
  SrtLyrics,
  chronie_from_text,
  delete_track_lyric,
  get_track_lyric,
  merge_lbl_chronie,
  save_track_lyric,
)
from chronograph.backend.lyrics.models.lbl_line_model import LblLineModel
from chronograph.backend.media import FileUntaggable
from chronograph.backend.player import Player
from chronograph.internal import Constants, Schema
from chronograph.ui.dialogs.resync_all_alert_dialog import ResyncAllAlertDialog
from chronograph.ui.widgets.lbl_sync_line import LblSyncLine
from chronograph.ui.widgets.ui_player import UIPlayer
from chronograph.utils.launch import launch_path
from dgutils import Actions
from dgutils.typing import unwrap

gtc = Gtk.Template.Child
logger = Constants.LOGGER
lrclib_logger = Constants.LRCLIB_LOGGER

PANGO_HIGHLIGHTER = Pango.AttrList.from_string("0 -1 weight ultrabold")


@Gtk.Template(resource_path=Constants.PREFIX + "/gtk/ui/sync_pages/LblSyncPage.ui")
@Actions.from_schema(Constants.PREFIX + "/resources/actions/lbl_sync_page_actions.yaml")
class LblSyncPage(Adw.NavigationPage):
  __gtype_name__ = "LblSyncPage"

  header_bar: Adw.HeaderBar = gtc()
  player_container: Gtk.Box = gtc()
  rew_button: Gtk.Button = gtc()
  forw_button: Gtk.Button = gtc()
  export_lyrics_button: Gtk.MenuButton = gtc()
  sync_lines_scrolled_window: Gtk.ScrolledWindow = gtc()
  sync_lines: Gtk.ListBox = gtc()
  selected_line: Optional[LblSyncLine] = None

  _autosave_timeout_id: Optional[int] = None

  def __init__(self, card_model: SongCardModel) -> None:
    def on_shown(*_args) -> None:
      if isinstance(self._file, FileUntaggable):
        self.action_set_enabled("controls.edit_metadata", enabled=False)

    super().__init__()
    self._card = card_model
    self._track_uuid = card_model.uuid
    self._file = card_model.media()
    self._card.bind_property(
      "title_display", self, "title", GObject.BindingFlags.SYNC_CREATE
    )
    if isinstance(self._file, FileUntaggable):
      self.action_set_enabled("controls.edit_metadata", enabled=False)
    self._player_widget = UIPlayer(card_model)
    self.player_container.append(self._player_widget)
    Player()._gst_player.connect("pos-upd", self._on_timestamp_changed)  # noqa: SLF001

    self.connect("showing", on_shown)
    self.connect("hidden", self._on_page_closed)
    self._close_rq_handler_id = Constants.WIN.connect(
      "close-request", self._on_app_close
    )

    # Automatically load lyrics from DB if available
    chronie = get_track_lyric(self._track_uuid)
    if chronie:
      self.sync_lines.remove_all()
      for line in chronie.lines:
        self._append_end_line(line_model=LblLineModel.from_chronie_line(line))

  @Gtk.Template.Callback()
  def _on_seek_button_released(self, button: Gtk.Button) -> None:
    display = Constants.WIN.get_display()
    seat = unwrap(display.get_default_seat())
    device = unwrap(seat.get_keyboard())
    state = device.get_modifier_state()

    direction = button == self.forw_button
    large = False

    if state in (Gdk.ModifierType.CONTROL_MASK.value, 20):  # 20 is used on X11
      large = True
    self._seek(None, None, direction, large)

  def is_all_lines_synced(self) -> bool:
    """Determines if all lines have timestamp

    Returns
    -------
    bool
      If all lines have timestamp
    """
    text = "\n".join([line.get_text() for line in self.sync_lines])  # ty:ignore[not-iterable]
    timestamp_pattern = re.compile(r"\[\d{2}:\d{2}\.\d{2,3}]")
    return all(timestamp_pattern.search(line) for line in text.strip().splitlines())

  ############### Line Actions ###############
  def _append_end_line(self, *_args, line_model: LblLineModel = LblLineModel()) -> None:  # noqa: B008
    self.sync_lines.append(LblSyncLine(line_model, self))
    self.sync_lines.set_visible(True)
    logger.debug("New line appended to the end of the sync lines")

  def append_line(self, *_args) -> None:
    """Append a new LBLSyncRow to a selected line"""
    if self.selected_line:
      for index, line in enumerate(self.sync_lines):  # ty:ignore[invalid-argument-type]
        if line == self.selected_line:
          self.sync_lines.insert(
            sync_line := LblSyncLine(LblLineModel(), self), index + 1
          )
          adj = self.sync_lines_scrolled_window.get_vadjustment()
          value = adj.get_value()
          sync_line.grab_focus()
          adj.set_value(value)
          self.sync_lines.set_visible(True)
          logger.debug("New line appended to selected line(%s)", self.selected_line)
          return

  def _prepend_line(self, *_args) -> None:
    if self.selected_line:
      for index, line in enumerate(self.sync_lines):  # ty:ignore[invalid-argument-type]
        if line == self.selected_line:
          try:
            self.sync_lines.insert(LblSyncLine(LblLineModel(), self), index)
            self.sync_lines.set_visible(True)  # Workaroud to fix ghosty shadow
            logger.debug(
              "New line prepended to selected line(%s)",
              self.selected_line,
            )
            return
          except IndexError:
            self.sync_lines.prepend(LblSyncLine(LblLineModel(), self))
            self.sync_lines.set_visible(True)  # Workaroud to fix ghosty shadow
            logger.debug("New line prepended to the list start")
            return

  def _remove_line(self, *_args) -> None:
    if self.selected_line:
      lines: list[LblSyncLine] = []
      for line in self.sync_lines:  # ty:ignore[not-iterable]
        lines.append(line)  # noqa: PERF402
      index = lines.index(self.selected_line)
      self.sync_lines.remove(self.selected_line)
      self.selected_line.link_teardown()
      if (row := self.sync_lines.get_row_at_index(index - 1)) is not None:
        row.grab_focus()
      else:
        self.sync_lines.set_visible(False)  # Workaroud to fix ghosty shadow
        self.selected_line = None
      logger.debug("Selected line(%s) removed", self.selected_line)

  ###############

  ############### Sync Actions ###############
  def _sync(self, *_args) -> None:
    if self.selected_line:
      ns = Player()._gst_player.props.position  # noqa: SLF001
      self.selected_line.model.starttimestamp = ns // 1_000_000  # ty:ignore[invalid-assignment]

      for index, line in enumerate(self.sync_lines):  # ty:ignore[invalid-argument-type]
        if (
          line == self.selected_line
          and (row := self.sync_lines.get_row_at_index(index + 1)) is not None
        ):
          row.grab_focus()
          return

  def _replay(self, *_args) -> None:
    Player().seek(self.selected_line.model.starttimestamp)  # ty:ignore[unresolved-attribute]

  def _seek(self, _action, _param, direction: bool, large: bool = False) -> None:
    self.selected_line = unwrap(self.selected_line)
    if direction:
      if not large:
        ms_seek = cast("int", Schema.get("root.settings.syncing.seek.lbl.def"))
      else:
        ms_seek = cast("int", Schema.get("root.settings.syncing.seek.lbl.large"))
    elif not large:
      ms_seek = cast("int", Schema.get("root.settings.syncing.seek.lbl.def")) * -1
    else:
      ms_seek = cast("int", Schema.get("root.settings.syncing.seek.lbl.large")) * -1
    ms = self.selected_line.model.starttimestamp  # ty:ignore[unresolved-attribute]
    ms = max(ms + ms_seek, 0)
    self.selected_line.model.starttimestamp = ms  # ty:ignore[invalid-assignment]
    Player().seek(ms)

  def resync_all(self, ms: int, backwards: bool = False) -> None:
    """Re-syncs all lines to a provided amount of milliseconds

    Parameters
    ----------
    ms : int
      Milliseconds
    backwards : bool, optional
      Is re-sync back, by default False
    """
    for line in self.sync_lines:  # ty:ignore[not-iterable]
      line_ms = line.model.starttimestamp
      line_ms = (line_ms - ms) if backwards else (line_ms + ms)
      line_ms = max(line_ms, 0)
      line.model.starttimestamp = line_ms
    logger.info(
      "All lines were resynced %sms %s",
      ms,
      "backwards" if backwards else "forward",
    )

  ###############

  ############### Import Actions ###############
  def _import_clipboard(self, *_args) -> None:
    def __on_clipboard_parsed(
      _clipboard, result: Gio.Task, clipboard: Gdk.Clipboard
    ) -> None:
      data = clipboard.read_text_finish(result)
      data = data or ""
      lyrics = chronie_from_text(data)
      self.sync_lines.remove_all()
      should_visible = False
      for line in lyrics.lines:
        self.sync_lines.append(LblSyncLine(LblLineModel.from_chronie_line(line), self))
        should_visible = True
      self.sync_lines.set_visible(should_visible)
      logger.info("Imported lyrics from clipboard")

    clipboard = unwrap(Gdk.Display().get_default()).get_clipboard()
    clipboard.read_text_async(None, __on_clipboard_parsed, user_data=clipboard)  # ty:ignore[unknown-argument]

  def _import_file(self, *_args) -> None:
    def on_selected_lyrics_file(file_dialog: Gtk.FileDialog, result: Gio.Task) -> None:
      path = unwrap(file_dialog.open_finish(result).get_path())

      self.sync_lines.remove_all()
      should_visible = False
      chronie = chronie_from_text(Path(path).read_text(encoding="utf-8"))
      for line in chronie.lines:
        self.sync_lines.append(LblSyncLine(LblLineModel.from_chronie_line(line), self))
        should_visible = True
      self.sync_lines.set_visible(should_visible)
      logger.info("Imported lyrics from file")

    dialog = Gtk.FileDialog(default_filter=Gtk.FileFilter(mime_types=["text/plain"]))
    dialog.open(Constants.WIN, None, on_selected_lyrics_file)

  def _import_lrclib(self, *_args) -> None:
    from chronograph.ui.dialogs.lrclib import LRClib

    lrclib_dialog = LRClib(self._card.title, self._card.artist, self._card.album)
    lrclib_dialog.present(Constants.WIN)
    logger.debug("LRClib import dialog shown")

  ###############

  ############### Export Actions ###############

  def _export_clipboard(self, *_args) -> None:
    string = ""
    for line in self.sync_lines:  # ty:ignore[not-iterable]
      string += line.get_text() + "\n"
    string = string.strip()
    clipboard = unwrap(Gdk.Display().get_default()).get_clipboard()
    clipboard.set(string)
    logger.info("Lyrics exported to clipboard")
    Constants.WIN.show_toast(_("Lyrics exported to clipboard"), timeout=3)

  def _export_file(self, _action, state: GLib.Variant) -> None:
    def on_export_file_selected(
      file_dialog: Gtk.FileDialog, result: Gio.Task, chronie: ChronieLyrics
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
        case ".lrc": lyr_format = LrcLyrics
        case ".srt": lyr_format = SrtLyrics
        case ".chron": lyr_format = ChronieLyrics
      # fmt: on
      text = lyr_format.from_chronie(chronie).to_file_text()
      Path(filepath).write_text(text, encoding="utf-8")
      logger.info("Lyrics exported to file: '%s'", filepath)

      Constants.WIN.show_toast(
        _("Lyrics exported to file"),
        button_label=_("Show"),
        button_callback=lambda *__: launch_path(Path(filepath)),
      )

    lyrics = "\n".join(line.get_text() for line in self.sync_lines).rstrip("\n")  # ty:ignore[not-iterable]
    chronie = chronie_from_text(lyrics)

    # fmt: off
    match str(state).strip("'"):
      case "plain": ext = ".txt"
      case "lrc": ext = ".lrc"
      case "srt": ext = ".srt"
      case "chron": ext = ".chron"
    # fmt: on

    format_filter = Gtk.FileFilter()
    if ext != ".chron":
      format_filter.set_name(_("Lyrics ({pattern})").format(pattern=ext))
    else:
      format_filter.set_name(_("Chronograph Project (.chron)"))
    format_filter.add_pattern(f"*{ext}")

    dialog = Gtk.FileDialog(
      initial_name=f"{self._card.artist_display} - {self._card.title_display}{ext}"
    )
    dialog.set_default_filter(format_filter)
    dialog.save(Constants.WIN, None, on_export_file_selected, chronie)

  ###############

  def _on_timestamp_changed(self, _obj, pos: int) -> None:
    try:
      lines: list[LblSyncLine] = []
      timestamps: list[int] = []
      for line in self.sync_lines:  # ty:ignore[not-iterable]
        line.set_attributes(None)
        if not line.get_text().strip():
          continue
        try:
          timing = timestamp_to_ns(line.get_text())
          lines.append(line)
          timestamps.append(timing)
        except ValueError:
          break

      if not timestamps:
        return

      timestamp = pos
      if timestamp < timestamps[0]:
        return
      for i in range(len(timestamps) - 1):
        if timestamps[i] <= timestamp < timestamps[i + 1]:
          lines[i].set_attributes(PANGO_HIGHLIGHTER)
          return
      if timestamp >= timestamps[-1]:
        lines[-1].set_attributes(PANGO_HIGHLIGHTER)
    except IndexError:
      pass

  ############### Utilities Actions ###############

  def _resync_all_lines(self, *_args) -> None:
    dialog = ResyncAllAlertDialog(self)
    dialog.present(Constants.WIN)
    unwrap(dialog.get_extra_child()).grab_focus()

  ###############

  ############### Autosave Actions ###############

  def reset_timer(self) -> None:
    """Resets throttling timer of `_autosave` call"""
    if self._autosave_timeout_id:
      GLib.source_remove(self._autosave_timeout_id)
    if Schema.get("root.settings.do-lyrics-db-updates.enabled"):
      self._autosave_timeout_id = GLib.timeout_add(
        cast("int", Schema.get("root.settings.do-lyrics-db-updates.throttling")) * 1000,
        self._autosave,
      )

  def _autosave(self) -> Literal[False]:
    if Schema.get("root.settings.do-lyrics-db-updates.enabled"):
      try:
        lyrics_lines = [
          cast("LblSyncLine", line).model.to_chronie_line() for line in self.sync_lines  # ty:ignore[unresolved-attribute, not-iterable]
        ]
        chronie = ChronieLyrics(lyrics_lines)
        if not chronie:
          delete_track_lyric(self._track_uuid)
          self._card.refresh_available_lyrics()
          self._autosave_timeout_id = None
          return False

        existing = get_track_lyric(self._track_uuid)
        chronie = merge_lbl_chronie(existing, chronie)
        save_track_lyric(self._track_uuid, chronie)

        self._card.refresh_available_lyrics()
        logger.debug("Lyrics autosaved successfully")
      except Exception:
        logger.warning("Autosave failed: %s", traceback.format_exc())
      self._autosave_timeout_id = None
    return False

  def _on_page_closed(self, *_args) -> None:
    Constants.WIN.disconnect(self._close_rq_handler_id)
    if self._autosave_timeout_id:
      GLib.source_remove(self._autosave_timeout_id)
    if Schema.get("root.settings.do-lyrics-db-updates.enabled"):
      logger.debug("Page closed, saving lyrics")
      self._autosave()
    Player().stop()
    self._player_widget.link_teardown()
    for line in self.sync_lines:  # ty:ignore[not-iterable]
      line.link_teardown()

  def _on_app_close(self, *_args) -> None:
    if self._autosave_timeout_id:
      GLib.source_remove(self._autosave_timeout_id)
    if Schema.get("root.settings.do-lyrics-db-updates.enabled"):
      logger.debug("App closed, saving lyrics")
      self._autosave()

  ###############

  ############### Publisher ###############

  def _publish(self, __, ___, card_model: SongCardModel) -> None:
    def on_publish_done(_service, status_code: int) -> None:
      nonlocal handler
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
      LRClibService().disconnect(handler)
      self.export_lyrics_button.set_sensitive(True)
      self.export_lyrics_button.set_icon_name("export-to-symbolic")

    def on_publish_failed(_service, error: Exception) -> None:
      nonlocal err_handler
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
      LRClibService().disconnect(err_handler)
      self.export_lyrics_button.set_sensitive(True)
      self.export_lyrics_button.set_icon_name("export-to-symbolic")

    lyrics_text = "\n".join(line.get_text() for line in self.sync_lines).rstrip("\n")  # ty:ignore[not-iterable]
    chronie = chronie_from_text(lyrics_text)
    lyrics_obj = LrcLyrics.from_chronie(chronie)
    plain_lyrics = PlainLyrics.from_chronie(chronie).text
    if not self.is_all_lines_synced():
      Constants.WIN.show_toast(
        _("Seems like not every line is synced"),
      )
      return
    self.export_lyrics_button.set_sensitive(False)
    self.export_lyrics_button.set_child(Adw.Spinner())

    try:
      handler = LRClibService().connect("publish-done", on_publish_done)
      err_handler = LRClibService().connect("publish-failed", on_publish_failed)
      LRClibService().publish(card_model.media(), plain_lyrics, lyrics_obj.text)
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
      return

  ###############

  def _show_info(self, *_args) -> None:
    from chronograph.ui.dialogs.about_file_dialog import AboutFileDialog

    AboutFileDialog(self._card).present(Constants.WIN)

  def _open_metadata_editor(self, *_args) -> None:
    from chronograph.ui.dialogs.metadata_editor import MetadataEditor

    MetadataEditor(self._card).present(Constants.WIN)

  def _embed_file(self, _action, state: GLib.Variant) -> None:
    from chronograph.window import MIME_TYPE_FILTERS

    def _on_file_selected(file_dialog: Gtk.FileDialog, result: Gio.Task) -> None:
      media_path = file_dialog.open_finish(result).get_path()
      if not media_path:
        return
      media = parse_file(media_path)
      if not media:
        return

      lyrics = "\n".join(line.get_text() for line in self.sync_lines).rstrip("\n")  # ty:ignore[not-iterable]
      if not lyrics.strip():
        return
      chronie = chronie_from_text(lyrics)
      media.embed_lyrics(chronie, str(state).strip("'"))

    dialog = Gtk.FileDialog(
      default_filter=MIME_TYPE_FILTERS[0],  # ty:ignore[invalid-argument-type]
      filters=MIME_TYPE_FILTERS,
    )
    dialog.open(Constants.WIN, None, _on_file_selected)
