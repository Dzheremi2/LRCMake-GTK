from pathlib import Path

from gi.repository import Gio

from chronograph.main import ChronographApplication
from chronograph.window import ChronographWindow  # type: ignore

APP_ID: str
VERSION: str
PREFIX: str

config_dir: Path
cache_dir: Path

schema: Gio.Settings
state_schema: Gio.Settings

app: ChronographApplication
win: ChronographWindow
