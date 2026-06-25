"""
Parse Wuthering Waves game logs to extract convene history credentials.

The game writes the convene webview URL to its log file whenever you open
the in-game convene history. We read that URL and pull out the auth params
needed to query Kuro's API.
"""

import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs


# Candidate log file locations (tried in order)
LOG_PATHS = [
    Path.home() / "AppData/Local/Kuro/KRGameTool/Saved/Logs/KRGameTool.log",
    Path.home() / "AppData/Local/Kuro Game/Wuthering Waves/Wuthering Waves Game/Client/Saved/Logs/Client.log",
]

CONVENE_URL_PATTERN = re.compile(
    r"(https://aki-gm-resources[^\s\"']+aki/gacha/index\.html[^\s\"']+record_id=[^\s\"']+)"
)


def find_log_file() -> Path | None:
    for path in LOG_PATHS:
        if path.exists():
            return path
    return None


def extract_credentials(log_path: Path) -> dict | None:
    """
    Scan the log file (from the end) for the most recent convene URL and
    return the parsed query parameters needed to hit Kuro's API.
    """
    text = log_path.read_text(encoding="utf-8", errors="ignore")
    matches = CONVENE_URL_PATTERN.findall(text)
    if not matches:
        return None

    url = matches[-1]  # most recent entry
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


def load_credentials() -> dict:
    """Return credentials or raise a clear error explaining what to do."""
    log = find_log_file()
    if log is None:
        raise RuntimeError(
            "Could not find Wuthering Waves log file.\n"
            "Make sure the game is installed and has been launched at least once."
        )

    creds = extract_credentials(log)
    if creds is None:
        raise RuntimeError(
            "Could not find your convene URL in the game logs.\n\n"
            "To fix this:\n"
            "  1. Launch Wuthering Waves\n"
            "  2. Open any Convene (gacha) history screen in-game\n"
            "  3. Wait a moment, then close it\n"
            "  4. Re-run this tool\n"
        )

    return creds
