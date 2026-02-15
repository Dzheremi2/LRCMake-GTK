from typing import cast

from gi.repository import GObject

from chronograph.backend.lyrics import ChronieLine
from chronograph.backend.lyrics.formats.utils import (
  TimeStampFormat,
  format_timestamp_ms,
)
from dgutils.typing import unwrap_or


class LblLineModel(GObject.Object):
  __gtype_name__ = "LblLineModel"

  text = cast("str", GObject.Property(type=str, default=""))

  _start_timestamp: int = -1
  _end_timestamp: int = -1

  def __init__(
    self, text: str = "", start_timestamp: int = -1, end_timestamp: int = -1
  ) -> None:
    super().__init__()
    self.props.text = text  # ty:ignore[unresolved-attribute]
    self._start_timestamp = start_timestamp
    self._end_timestamp = end_timestamp

  @classmethod
  def from_chronie_line(cls, line: ChronieLine) -> "LblLineModel":
    text = line.line
    start = -1
    end = -1
    if line.timings is not None:
      start = unwrap_or(line.timings.start, -1)
      end = unwrap_or(line.timings.end, -1)
    return cls(text, start, end)

  @GObject.Property(type=str)
  def startprecise(self) -> str:
    if self._start_timestamp != -1:
      return format_timestamp_ms(self._start_timestamp, TimeStampFormat.LRC)
    return ""

  @GObject.Property(type=str)
  def start(self) -> str:
    if self._start_timestamp != -1:
      return format_timestamp_ms(
        self._start_timestamp, TimeStampFormat.LRC, precise=False
      )
    return ""

  @start.setter
  def start(self, ms: int) -> None:
    self._start_timestamp = ms
    self.notify("startprecise")

  @GObject.Property(type=str)
  def endprecise(self) -> str:
    if self._end_timestamp != -1:
      return format_timestamp_ms(self._end_timestamp, TimeStampFormat.LRC)
    return ""

  @GObject.Property(type=str)
  def end(self) -> str:
    if self._end_timestamp != -1:
      return format_timestamp_ms(
        self._end_timestamp, TimeStampFormat.LRC, precise=False
      )
    return ""

  @end.setter
  def end(self, ms: int) -> None:
    self._end_timestamp = ms
    self.notify("endprecise")
