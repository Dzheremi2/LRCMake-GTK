from binascii import unhexlify
import hashlib
import requests
import eyed3 # type: ignore

from gi.repository import Adw # type: ignore

from lrcmake.methods.exportData import prepare_plain_lyrics, prepare_synced_lyrics
from lrcmake import shared

def verify_nonce(result, target):
    if len(result) != len(target):
        return False

    for i in range(len(result)):
        if result[i] > target[i]:
            return False
        elif result[i] < target[i]:
            break

    return True

def solve_challenge(prefix, target_hex):
    target = unhexlify(target_hex.upper())
    nonce = 0

    while True:
        input_data = f"{prefix}{nonce}".encode()
        hashed = hashlib.sha256(input_data).digest()

        if verify_nonce(hashed, target):
            break
        else:
            nonce += 1

    return str(nonce)

def do_publish(*args):
    if (shared.win.title or shared.win.artist or eyed3.load(shared.win.filepath).tag.album) == "Unknown":
        toast = Adw.Toast(title=_("Some of Title, Artist and/or Album fileds are Unknown!")) # type: ignore
        shared.win.toast_overlay.add_toast(toast)
        shared.win.export_lyrics.set_icon_name("export-to-symbolic")
        raise AttributeError("Some of Title, Artist and/or Album fileds are Unknown!")
    challenge_data = requests.post(url="https://lrclib.net/api/request-challenge")
    challenge_data_json = challenge_data.json()
    nonce = solve_challenge(prefix=challenge_data_json['prefix'], target_hex=challenge_data_json['target'])
    print(f"X-Publish-Token: {challenge_data_json['prefix']}:{nonce}")
    response = requests.post(
        url="https://lrclib.net/api/publish",
        headers={"X-Publish-Token": f"{challenge_data_json['prefix']}:{nonce}", "Content-Type": "application/json"},
        params={'keep_headers': 'true'},
        json={
            "trackName": shared.win.title,
            "artistName": shared.win.artist,
            "albumName": eyed3.load(shared.win.filepath).tag.album,
            "duration": int(eyed3.load(shared.win.filepath).info.time_secs),
            "plainLyrics": prepare_plain_lyrics(),
            "syncedLyrics": prepare_synced_lyrics()
        }
    )
    print(response.status_code)
    shared.win.export_lyrics.set_icon_name("export-to-symbolic")
    if response.status_code == 201:
        toast = Adw.Toast(title=_("Published successfully: ") + str(response.status_code)) # type: ignore
        shared.win.toast_overlay.add_toast(toast)
    elif response.status_code == 400:
        toast = Adw.Toast(title=_("Incorrect publish token: ") + str(response.status_code)) # type: ignore
        shared.win.toast_overlay.add_toast(toast)
    else:
        toast = Adw.Toast(title=_("Unknown error occured: ") + str(response.status_code)) # type: ignore
        shared.win.toast_overlay.add_toast(toast)