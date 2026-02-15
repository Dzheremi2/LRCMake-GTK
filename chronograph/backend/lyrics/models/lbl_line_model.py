from gi.repository import GObject

from chronograph.backend.lyrics import ChronieLine, ChronieTimings
from chronograph.backend.lyrics.formats.utils import (
  TimeStampFormat,
  format_timestamp_ms,
)
from dgutils.typing import unwrap_or


class LblLineModel(GObject.Object):
  __gtype_name__ = "LblLineModel"

  text = GObject.Property(type=str, default="")

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

  def to_chronie_line(self) -> ChronieLine:
    start = self.starttimestamp if self.starttimestamp != -1 else None
    end = self.endtimestamp if self.endtimestamp != -1 else None
    timings = ChronieTimings(start, end)
    if start is None and end is None:
      timings = None
    return ChronieLine(self.text, timings)

  @GObject.Property(type=str, default="")
  def startprecisedisplay(self) -> str:
    if self._start_timestamp != -1:
      return format_timestamp_ms(self._start_timestamp, TimeStampFormat.LRC)
    return ""

  @GObject.Property(type=str, default="")
  def startdisplay(self) -> str:
    if self._start_timestamp != -1:
      return format_timestamp_ms(
        self._start_timestamp, TimeStampFormat.LRC, precise=False
      )
    return ""

  @GObject.Property(type=GObject.TYPE_INT64, default=-1)
  def starttimestamp(self) -> int:
    return self._start_timestamp

  @starttimestamp.setter
  def starttimestamp(self, ms: int) -> None:
    self._start_timestamp = ms
    self.notify("startprecisedisplay")
    self.notify("startdisplay")

  @GObject.Property(type=str, default="")
  def endprecisedisplay(self) -> str:
    if self._end_timestamp != -1:
      return format_timestamp_ms(self._end_timestamp, TimeStampFormat.LRC)
    return ""

  @GObject.Property(type=str, default="")
  def enddisplay(self) -> str:
    if self._end_timestamp != -1:
      return format_timestamp_ms(
        self._end_timestamp, TimeStampFormat.LRC, precise=False
      )
    return ""

  @GObject.Property(type=GObject.TYPE_INT64, default=-1)
  def endtimestamp(self) -> int:
    return self._end_timestamp

  @endtimestamp.setter
  def endtimestamp(self, ms: int) -> None:
    self._end_timestamp = ms
    self.notify("endprecisedisplay")
    self.notify("enddisplay")
