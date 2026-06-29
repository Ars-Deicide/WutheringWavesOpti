"""Per-user credential and convene cache storage (keyed by Discord user ID)."""

import json
import time
from pathlib import Path

USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"
CACHE_FILE = Path(__file__).parent.parent / "data" / "convene_cache.json"
CACHE_TTL  = 300

USERS_FILE.parent.mkdir(exist_ok=True)


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text()) if path.exists() else {}
    except Exception:
        return {}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))


def get_creds(user_id: int) -> dict | None:
    return _load(USERS_FILE).get(str(user_id))


def set_creds(user_id: int, creds: dict) -> None:
    data = _load(USERS_FILE)
    data[str(user_id)] = creds
    _save(USERS_FILE, data)


def get_cache(user_id: int, pools: list[int]) -> dict | None:
    data = _load(CACHE_FILE)
    entry = data.get(str(user_id))
    if not entry:
        return None
    if time.time() - entry.get("ts", 0) > CACHE_TTL:
        return None
    if not all(str(p) in entry.get("pools", {}) for p in pools):
        return None
    return entry


def set_cache(user_id: int, results: dict) -> None:
    from wuwa.convene import ConveneRecord
    from dataclasses import asdict
    data = _load(CACHE_FILE)
    data[str(user_id)] = {
        "ts": time.time(),
        "pools": {
            str(pid): [asdict(r) for r in records]
            for pid, records in results.items()
        }
    }
    _save(CACHE_FILE, data)


def load_cache_results(user_id: int) -> dict | None:
    from wuwa.convene import ConveneRecord
    data = _load(CACHE_FILE)
    entry = data.get(str(user_id))
    if not entry:
        return None
    return {
        int(pid): [ConveneRecord(**r) for r in records]
        for pid, records in entry["pools"].items()
    }
