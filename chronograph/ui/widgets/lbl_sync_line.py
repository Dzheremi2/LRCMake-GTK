from typing import TYPE_CHECKING

from chronograph.internal import Constants

if TYPE_CHECKING:
  from chronograph.ui.sync_pages.lbl_sync_page import LblSyncPage
from typing import cast

from gi.repository import Adw, GObject, Gtk

from chronograph.backend.lyrics.models.lbl_line_model import LblLineModel
from dgutils import Actions, Linker


@Actions.from_schema(Constants.PREFIX + "/resources/actions/lbl_sync_line_actions.yaml")
class LblSyncLine(Adw.EntryRow, Linker):
  __gtype_name__ = "LblSyncLine"

  def __init__(self, model: LblLineModel, sync_page: "LblSyncPage") -> None:
    super().__init__(editable=True)
    Linker.__init__(self)
    self.model = model
    self.page = sync_page
    self.add_css_class("property")

    self.new_binding(
      self.model.bind_property("text", self, "text", GObject.BindingFlags.SYNC_CREATE)
    )
    self.new_connection(self.model, "notify::startprecisedisplay", self._build_title)
    self.new_connection(self.model, "notify::endprecisedisplay", self._build_title)
    self._build_title(self.model)

    self.focus_controller = Gtk.EventControllerFocus()
    self.new_connection(self.focus_controller, "enter", self._on_selected)
    self.add_controller(self.focus_controller)

    # Extract Gtk.Text from EntryRow to connect for on backspace press line deletion
    for item in self.get_child():  # ty:ignore[not-iterable]
      for _item in item:
        if isinstance(_item, Gtk.Text):
          self.text_field = _item
          menu = Gtk.Builder.new_from_resource(
            Constants.PREFIX + "/models/LblSyncLineExtraMenu.ui"
          ).get_object("timestamp_actions")
          self.text_field.set_property("extra-menu", menu)
          break

    self.new_connection(self.text_field, "backspace", self._remove_line_on_backspace)
    self.new_connection(self, "entry-activated", self._add_line_on_enter)

  def link_teardown(self) -> None:
    Linker.link_teardown(self)
    self.page = None
    self.model = None

  def _add_line_on_enter(self, *_args) -> None:
    self.page.append_line()

  def _remove_line_on_backspace(self, text: Gtk.Text) -> None:
    if text.get_text_length() == 0:
      lines: list[LblSyncLine] = []
      for line in self.page.sync_lines:  # ty:ignore[not-iterable]
        lines.append(line)  # noqa: PERF402
      index = lines.index(self)
      self.page.sync_lines.remove(self)
      if (row := self.page.sync_lines.get_row_at_index(index - 1)) is not None:
        row.grab_focus()
      else:
        self.page.sync_lines.set_visible(False)  # Workaroud to fix ghosty shadow

  def _on_selected(self, *_args) -> None:
    cast("LblSyncPage", self.page).selected_line = cast("LblSyncLine", self)

  def _reset_timer(self, *_args) -> None:
    self.page.reset_timer()

  def _build_title(self, model: LblLineModel, *_args) -> None:
    end = cast("str", model.endprecisedisplay)
    start = cast("str", model.startprecisedisplay)
    if start == "" and end == "":
      title = _("Not synced yet")
    elif start != "" and end == "":
      title = _("{start} — End is not synced").format(start=start)
    elif start == "" and end != "":
      title = _("Start is not synced — {end}").format(end=end)
    else:
      title = f"{start} — {end}"
    self.set_title(title)

  def _clear_ts(self, _action, _pspec, ts_position: str) -> None:
    if ts_position == "start":
      self.model.starttimestamp = -1  # ty:ignore[invalid-assignment]
    if ts_position == "end":
      self.model.endtimestamp = -1  # ty:ignore[invalid-assignment]
    if ts_position == "all":
      self.model.starttimestamp = -1  # ty:ignore[invalid-assignment]
      self.model.endtimestamp = -1  # ty:ignore[invalid-assignment]
