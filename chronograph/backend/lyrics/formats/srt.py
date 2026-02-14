import re

from chronograph.backend.lyrics import ChronieLine, ChronieTimings
from chronograph.backend.lyrics.chronie.chronie_lyrics import ChronieLyrics
from chronograph.backend.lyrics.formats.utils import (
  TimeStampFormat,
  format_timestamp_ms,
)
from chronograph.backend.lyrics.interfaces import LyricFormat
from dgutils.typing import unwrap_or


def _srt_timestamp_to_ms(timestamp: str) -> int:
  separated = re.split(r"[:,]", timestamp)
  ints = tuple(int(s) for s in separated)
  return ((ints[0] * 60 + ints[1]) * 60 + ints[2]) * 1000 + ints[3]


class SrtLyrics(LyricFormat):
  format = "srt"
  _SRT_BLOCK = re.compile(
    r"(?P<idx>\d+)\n(?P<tsS>(?P<stH>\d{1,2}):(?P<stM>\d{1,2}):(?P<stS>\d{1,2}),(?P<stMS>\d{1,3}))\s-->\s(?P<tsE>(?P<endH>\d{1,2}):(?P<endM>\d{1,2}):(?P<endS>\d{1,2}),(?P<endMS>\d{1,3}))\n(?P<text>.*)"
  )

  def __init__(self, text: str = "") -> None:
    self._text = text

  @classmethod
  def from_chronie(cls, chronie: ChronieLyrics) -> "SrtLyrics":
    lyrics = ""
    # used for storing srt blocks in format of "index", "start timestamp", "end", "text"
    blocks: tuple[list[int], list[str], list[str], list[str]] = ([], [], [], [])
    for idx, line in enumerate(chronie.lines):
      block_index = idx + 1
      timings = unwrap_or(line.timings, ChronieTimings(0, 0))
      start = unwrap_or(timings.start, 0)
      if timings.end is None:
        try:
          end = unwrap_or(
            unwrap_or(chronie.lines[idx + 1].timings, ChronieTimings(0)).start, 0
          )
        except IndexError:
          end = unwrap_or(timings.start, 0)
      else:
        end = timings.end
      text = line.line
      blocks[0].append(block_index)
      blocks[1].append(format_timestamp_ms(start, TimeStampFormat.SRT))
      blocks[2].append(format_timestamp_ms(end, TimeStampFormat.SRT))
      blocks[3].append(text)

    for block, start, end, text in zip(
      blocks[0], blocks[1], blocks[2], blocks[3], strict=True
    ):
      line_timestamp = f"{start} --> {end}"
      lyrics += f"{block}\n{line_timestamp}\n{text}\n\n"
    return SrtLyrics(lyrics.strip())

  @property
  def text(self) -> str:
    return self._text

  def is_finished(self) -> bool:
    return True

  def to_file_text(self) -> str:
    return self.text

  def to_chronie(self) -> ChronieLyrics:
    lines: list[ChronieLine] = []
    for match in self._SRT_BLOCK.finditer(self.text):
      sth = match.group("stH")
      stm = match.group("stM")
      sts = match.group("stS")
      stms = match.group("stMs")
      start_corrupted = any(item is None for item in (sth, stm, sts, stms))

      endh = match.group("endH")
      endm = match.group("endM")
      ends = match.group("endS")
      endms = match.group("endMs")
      end_corrupted = any(item is None for item in (endh, endm, ends, endms))

      text = match.group("text")

      if start_corrupted:
        start_whole = 0
      else:
        sh = int(sth)
        sm = int(stm)
        ss = int(sts)
        sms = int(stms)
        start_whole = ((sh * 60 + sm) * 60 + ss) * 1000 + sms

      if end_corrupted:
        end_whole = 0
      else:
        eh = int(sth)
        em = int(stm)
        es = int(sts)
        ems = int(stms)
        end_whole = ((eh * 60 + em) * 60 + es) * 1000 + ems

      line = ChronieLine(text, ChronieTimings(start_whole, end_whole))
      lines.append(line)

    return ChronieLyrics(lines)
