"""
Parse Wuthering Waves game logs to extract convene history credentials,
or load them from a saved config file (set via `python main.py link --url`).
"""

import json
import re
from pathlib import Path
from urllib.parse import parse_qs

CACHE_FILE = Path(__file__).parent.parent / ".credentials.json"

LOG_PATHS = [
    Path.home() / "AppData/Local/Kuro/KRGameTool/Saved/Logs/KRGameTool.log",
    Path.home() / "AppData/Local/Kuro Game/Wuthering Waves/Wuthering Waves Game/Client/Saved/Logs/Client.log",
    Path("C:/Program Files/Wuthering Waves/Wuthering Waves Game/Client/Saved/Logs/Client.log"),
    Path("C:/Program Files (x86)/Wuthering Waves/Wuthering Waves Game/Client/Saved/Logs/Client.log"),
]

CONVENE_URL_PATTERN = re.compile(
    r"(https://aki-gm-resources[^\s\"']+aki/gacha/index\.html[^\s\"']+record_id=[^\s\"']+)"
)


def parse_convene_url(url: str) -> dict | None:
    """Parse a convene webview URL and return credential dict, or None if invalid."""
    if "#/record?" not in url:
        return None
    fragment = url.split("#/record?", 1)[-1]
    params = {k: v[0] for k, v in parse_qs(fragment).items()}
    required = {"svr_id", "player_id", "record_id"}
    if not required.issubset(params):
        return None
    return {
        "server_id": params["svr_id"],
        "player_id": params["player_id"],
        "record_id": params["record_id"],
        "lang": params.get("lang", "en"),
        "svr_area": params.get("svr_area", "global"),
    }


def save_credentials(creds: dict) -> None:
    CACHE_FILE.write_text(json.dumps(creds, indent=2))


def load_cached_credentials() -> dict | None:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return None


def extract_from_logs() -> dict | None:
    """Try to find the convene URL in game log files (multiple encodings)."""
    for log_path in LOG_PATHS:
        if not log_path.exists():
            continue
        raw = log_path.read_bytes()
        for encoding in ("utf-8", "utf-16-le", "utf-16-be", "latin-1"):
            try:
                text = raw.decode(encoding, errors="replace")
                matches = CONVENE_URL_PATTERN.findall(text)
                if matches:
                    return parse_convene_url(matches[-1])
            except Exception:
                continue
    return None


def load_credentials() -> dict:
    """Return credentials from cache, logs, or raise a helpful error."""
    cached = load_cached_credentials()
    if cached:
        return cached

    from_logs = extract_from_logs()
    if from_logs:
        save_credentials(from_logs)
        return from_logs

    raise RuntimeError(
        "No saved credentials found.\n\n"
        "Run this to link your account manually:\n"
        "  python main.py link --url \"YOUR_CONVENE_URL\"\n\n"
        "To get your convene URL:\n"
        "  See: python main.py link --how\n"
    )
