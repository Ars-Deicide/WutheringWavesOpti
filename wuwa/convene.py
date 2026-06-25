"""
Fetch convene (gacha) history from Kuro's official API.

Kuro exposes the same endpoint the in-game webview uses, so this is
identical to what the game itself requests — no scraping or reverse
engineering involved.
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

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


@dataclass
class ConveneRecord:
    name: str
    type: str          # "Resonator" or "Weapon"
    rarity: int
    pool_type: int
    pull_time: str
    pull_number: int   # sequential pull index within the session


def fetch_pool(creds: dict, pool_type: int, page_size: int = 20) -> list[ConveneRecord]:
    """Fetch all records for a single banner pool, handling pagination."""
    endpoint = API_ENDPOINTS.get(creds.get("svr_area", "global"), API_ENDPOINTS["global"])
    records: list[ConveneRecord] = []
    last_id = "0"
    pull_index = 0

    while True:
        payload = {
            "cardPoolId":   last_id,
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

        items = data.get("data", [])
        if not items:
            break

        for item in items:
            pull_index += 1
            records.append(ConveneRecord(
                name=item.get("name", "Unknown"),
                type=item.get("resourceType", ""),
                rarity=int(item.get("qualityLevel", 3)),
                pool_type=pool_type,
                pull_time=item.get("time", ""),
                pull_number=pull_index,
            ))

        last_id = items[-1].get("id", "0")
        time.sleep(0.05)

        if len(items) < page_size:
            break

    return records


def fetch_all(creds: dict, pools: list[int] | None = None) -> dict[int, list[ConveneRecord]]:
    """Fetch records for all pool types in parallel."""
    pools = pools or list(POOL_TYPES.keys())
    results: dict[int, list[ConveneRecord]] = {}
    with ThreadPoolExecutor(max_workers=len(pools)) as executor:
        futures = {executor.submit(fetch_pool, creds, p): p for p in pools}
        for future in as_completed(futures):
            pool_type = futures[future]
            results[pool_type] = future.result()
    return results


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
