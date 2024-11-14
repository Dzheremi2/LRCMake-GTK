from binascii import unhexlify
import hashlib
import requests
import eyed3
from . import main
from .exportData import prepare_plain_lyrics, prepare_synced_lyrics

async def verify_nonce(result, target):
    if len(result) != len(target):
        return False

    for i in range(len(result)):
        if result[i] > target[i]:
            return False
        elif result[i] < target[i]:
            break

    return True

async def solve_challenge(prefix, target_hex):
    target = unhexlify(target_hex.upper())
    nonce = 0

    while True:
        input_data = f"{prefix}{nonce}".encode()
        hashed = hashlib.sha256(input_data).digest()

        if await verify_nonce(hashed, target):
            break
        else:
            nonce += 1

    return str(nonce)

async def do_publish(*args):
    challenge_data = requests.post(url="https://lrclib.net/api/request-challenge")
    challenge_data_json = challenge_data.json()
    nonce = await solve_challenge(prefix=challenge_data_json['prefix'], target_hex=challenge_data_json['target'])
    print(f"X-Publish-Token: {challenge_data_json['prefix']}:{nonce}")
    response = requests.post(
        url="https://lrclib.net/api/publish",
        headers={"X-Publish-Token": f"{challenge_data_json['prefix']}:{nonce}", "Content-Type": "application/json"},
        params={'keep_headers': 'true'},
        json={
            "trackName": main.app.win.title,
            "artistName": main.app.win.artist,
            "albumName": eyed3.load(main.app.win.filepath).tag.album,
            "duration": int(eyed3.load(main.app.win.filepath).info.time_secs),
            "plainLyrics": prepare_plain_lyrics(),
            "syncedLyrics": prepare_synced_lyrics()
        }
    )
    print(response.status_code)