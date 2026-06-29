"""
Fetch convene (gacha) history from Kuro's official API.

Kuro exposes the same endpoint the in-game webview uses, so this is
identical to what the game itself requests — no scraping or reverse
engineering involved.
"""

import json
import time
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

CACHE_FILE = Path(__file__).parent.parent / ".convene_cache.json"
CACHE_TTL  = 300  # seconds before re-fetching from API

# Kuro's official gacha query endpoints
API_ENDPOINTS = {
    "global": "https://gmserver-api.aki-game2.net/gacha/record/query",
    "cn":     "https://gmserver-api.aki-game2.com/gacha/record/query",
}

# Banner pool types as defined by Kuro
POOL_TYPES = {
    1: "Featured Resonator",
    2: "Featured Weapon",
    3: "Standard Resonator",
    4: "Standard Weapon",
    5: "Beginner's Banner",
    6: "Beginner's Choice",
    7: "Giveback Custom",
}

RARITY_COLOR = {5: "gold", 4: "purple", 3: "blue"}

# ---------------------------------------------------------------------------
# Time-limited collaboration banners
# ---------------------------------------------------------------------------
# Collab banners should only be selectable while the event is live. Populate
# COLLAB_POOLS with the real Kuro cardPoolType IDs + display names; they auto-
# hide once time.time() passes COLLAB_ENDS_AT. Leave COLLAB_POOLS empty to show
# only the standard banners.
COLLAB_ENDS_AT = 1783591555  # 2026-07-09 ~11:05 (10d 11h from 2026-06-29 setup)
COLLAB_POOLS: dict[int, str] = {
    # NOTE: pool IDs (8–11) are assumed sequential — display/gating works
    # regardless, but fetching needs Kuro's real cardPoolType numbers. Update
    # these if Fetch returns empty for a collab banner.
    8:  "Dreaming Upon the Moon",
    9:  "Rekindled Embers of Rage",
    10: "Absolute Pulsation - Spectral Trigger",
    11: "Absolute Pulsation - Skull Thrasher",
}


def collab_active() -> bool:
    """True only while the collaboration event is live AND banners are configured."""
    return bool(COLLAB_POOLS) and time.time() < COLLAB_ENDS_AT


def available_pools() -> dict[int, str]:
    """Standard banners, plus collab banners only while the event is live."""
    pools = dict(POOL_TYPES)
    if collab_active():
        pools.update(COLLAB_POOLS)
    return pools


@dataclass
class ConveneRecord:
    name: str
    type: str          # "Resonator" or "Weapon"
    rarity: int
    pool_type: int
    pull_time: str
    pull_number: int   # sequential pull index within the session


def fetch_pool(creds: dict, pool_type: int) -> list[ConveneRecord]:
    """Fetch all records for a single banner pool.

    Kuro's gacha endpoint returns the pool's *entire* history in one response —
    there is no cursor pagination. The previous version looped on `cardPoolId`
    as if it were a cursor, but the API ignores it and returns the full list
    every call, so the loop never terminated (len(items) stayed >= page_size)
    and effectively hung. A single POST is all that's needed.
    """
    endpoint = API_ENDPOINTS.get(creds.get("svr_area", "global"), API_ENDPOINTS["global"])
    payload = {
        "cardPoolId":   "0",
        "cardPoolType": pool_type,
        "languageCode": creds.get("lang", "en"),
        "playerId":     creds["player_id"],
        "recordId":     creds["record_id"],
        "serverId":     creds["server_id"],
    }

    resp = requests.post(endpoint, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if data.get("code") != 0:
        raise RuntimeError(f"API error {data.get('code')}: {data.get('message')}")

    records: list[ConveneRecord] = []
    for pull_index, item in enumerate(data.get("data", []), start=1):
        records.append(ConveneRecord(
            name=item.get("name", "Unknown"),
            type=item.get("resourceType", ""),
            rarity=int(item.get("qualityLevel", 3)),
            pool_type=pool_type,
            pull_time=item.get("time", ""),
            pull_number=pull_index,
        ))

    return records


def _load_cache() -> dict | None:
    try:
        if not CACHE_FILE.exists():
            return None
        data = json.loads(CACHE_FILE.read_text())
        if time.time() - data.get("ts", 0) > CACHE_TTL:
            return None
        return data
    except Exception:
        return None


def _save_cache(results: dict[int, list[ConveneRecord]]) -> None:
    try:
        serializable = {
            "ts": time.time(),
            "pools": {
                str(pool_id): [asdict(r) for r in records]
                for pool_id, records in results.items()
            }
        }
        CACHE_FILE.write_text(json.dumps(serializable))
    except Exception:
        pass


def _from_cache(data: dict) -> dict[int, list[ConveneRecord]]:
    return {
        int(pool_id): [ConveneRecord(**r) for r in records]
        for pool_id, records in data["pools"].items()
    }


def fetch_all(creds: dict, pools: list[int] | None = None, force: bool = False) -> tuple[dict[int, list[ConveneRecord]], bool]:
    """
    Fetch records for all pool types in parallel.
    Returns (results, from_cache). Uses cache unless force=True or cache is stale.
    """
    pools = pools or list(POOL_TYPES.keys())

    if not force:
        cached = _load_cache()
        if cached:
            all_present = all(str(p) in cached["pools"] for p in pools)
            if all_present:
                return _from_cache(cached), True

    results: dict[int, list[ConveneRecord]] = {}
    with ThreadPoolExecutor(max_workers=len(pools)) as executor:
        futures = {executor.submit(fetch_pool, creds, p): p for p in pools}
        for future in as_completed(futures):
            pool_type = futures[future]
            results[pool_type] = future.result()

    _save_cache(results)
    return results, False


def pity_stats(records: list[ConveneRecord]) -> dict:
    """Calculate current pity and 5★ rate from a pool's record list."""
    since_last_5 = 0
    since_last_4 = 0
    total_5 = sum(1 for r in records if r.rarity == 5)
    total_pulls = len(records)

    for r in records:
        if r.rarity == 5:
            break
        since_last_5 += 1
    for r in records:
        if r.rarity >= 4:
            break
        since_last_4 += 1

    return {
        "current_pity_5": since_last_5,
        "current_pity_4": since_last_4,
        "total_pulls": total_pulls,
        "total_5star": total_5,
        "rate_5star": round(total_5 / total_pulls * 100, 2) if total_pulls else 0,
    }
