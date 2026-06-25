"""
Echo scoring and build optimization.

Echoes are Wuthering Waves' artifact equivalent. Each echo has a main stat
and up to 5 sub-stats. We score them using per-resonator stat weights so
you can instantly tell which echoes are worth keeping.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Stat weights per resonator archetype
# Higher weight = more valuable for that playstyle
# ---------------------------------------------------------------------------
ARCHETYPES: dict[str, dict[str, float]] = {
    "crit_dps": {
        "CRIT Rate":        1.0,
        "CRIT DMG":         1.0,
        "ATK%":             0.75,
        "Flat ATK":         0.3,
        "Energy Regen":     0.2,
        "HP%":              0.1,
        "Flat HP":          0.05,
        "DEF%":             0.05,
        "Flat DEF":         0.02,
    },
    "atk_dps": {
        "ATK%":             1.0,
        "CRIT Rate":        0.9,
        "CRIT DMG":         0.9,
        "Flat ATK":         0.4,
        "Energy Regen":     0.25,
        "HP%":              0.1,
        "Flat HP":          0.05,
        "DEF%":             0.05,
        "Flat DEF":         0.02,
    },
    "support": {
        "Energy Regen":     1.0,
        "HP%":              0.85,
        "Flat HP":          0.4,
        "ATK%":             0.3,
        "CRIT Rate":        0.2,
        "CRIT DMG":         0.2,
        "DEF%":             0.15,
        "Flat DEF":         0.07,
        "Flat ATK":         0.05,
    },
    "tank": {
        "DEF%":             1.0,
        "HP%":              0.9,
        "Flat HP":          0.45,
        "Flat DEF":         0.4,
        "Energy Regen":     0.5,
        "ATK%":             0.1,
        "CRIT Rate":        0.1,
        "CRIT DMG":         0.1,
        "Flat ATK":         0.02,
    },
}

# Resonator → archetype mapping
RESONATOR_ARCHETYPES: dict[str, str] = {
    # --- Aero ---
    "Aalto":            "atk_dps",
    "Jiyan":            "crit_dps",
    "Jianxin":          "tank",
    "Yangyang":         "support",
    # --- Electro ---
    "Calcharo":         "crit_dps",
    "Mortefi":          "crit_dps",
    "Xiangli Yao":      "crit_dps",
    "Yuanwu":           "support",
    "Zani":             "support",
    # --- Fusion ---
    "Brant":            "atk_dps",
    "Changli":          "crit_dps",
    "Chixia":           "atk_dps",
    "Encore":           "atk_dps",
    # --- Glacio ---
    "Baizhi":           "support",
    "Carlotta":         "crit_dps",
    "Hiyuki":           "crit_dps",
    "Lingyang":         "crit_dps",
    "Sanhua":           "crit_dps",
    # --- Havoc ---
    "Camellya":         "crit_dps",
    "Cantarella":       "crit_dps",
    "Danjin":           "crit_dps",
    "Roccia":           "support",
    "Rover (Havoc)":    "crit_dps",
    "Taoqi":            "tank",
    # --- Spectro ---
    "Jinhsi":           "atk_dps",
    "Phoebe":           "crit_dps",
    "Rover (Spectro)":  "crit_dps",
    "The Shorekeeper":  "support",
    "Verina":           "support",
    # --- Additional released resonators ---
    "Aemeath":          "crit_dps",
    "Augusta":          "support",
    "Buling":           "atk_dps",
    "Cartethyia":       "crit_dps",
    "Chisa":            "crit_dps",
    "Ciaccona":         "support",
    "Denia":            "crit_dps",
    "Galbrena":         "support",
    "Iuno":             "support",
    "Lucilla":          "crit_dps",
    "Lucy":             "support",
    "Lumi":             "support",
    "Lupa":             "crit_dps",
    "Luuk Herssen":     "crit_dps",
    "Lynae":            "support",
    "Mornye":           "crit_dps",
    "Phrolova":         "crit_dps",
    "Qiuyuan":          "support",
    "Rebecca":          "crit_dps",
    "Rover (Aero)":     "atk_dps",
    "Sigrika":          "tank",
}

VALID_STATS = list(ARCHETYPES["crit_dps"].keys())

ECHO_SLOTS = 5
MAX_SCORE = 100.0


@dataclass
class EchoSubstat:
    stat: str
    value: float


@dataclass
class Echo:
    slot: int                          # 1–5
    main_stat: str
    substats: list[EchoSubstat] = field(default_factory=list)
    name: str = ""


def score_echo(echo: Echo, archetype: str) -> float:
    """
    Score a single echo 0–100 based on how valuable its substats are
    for the given archetype. Main stat contributes a fixed 30 points.
    """
    weights = ARCHETYPES.get(archetype, ARCHETYPES["crit_dps"])

    # Main stat contribution (fixed 30 pts if it's a desired stat)
    main_weight = weights.get(echo.main_stat, 0)
    main_score = 30.0 * main_weight

    # Substats contribute up to 70 pts
    sub_score = 0.0
    for sub in echo.substats[:5]:
        sub_score += weights.get(sub.stat, 0) * 14.0  # 5 substats × 14 = 70 max

    total = main_score + sub_score
    return round(min(total, MAX_SCORE), 1)


def grade(score: float) -> str:
    if score >= 85:
        return "S"
    if score >= 70:
        return "A"
    if score >= 50:
        return "B"
    if score >= 30:
        return "C"
    return "D"


def score_build(echoes: list[Echo], resonator: str) -> list[dict]:
    archetype = RESONATOR_ARCHETYPES.get(resonator, "crit_dps")
    results = []
    for echo in echoes:
        s = score_echo(echo, archetype)
        results.append({
            "slot":      echo.slot,
            "name":      echo.name or f"Echo {echo.slot}",
            "main_stat": echo.main_stat,
            "score":     s,
            "grade":     grade(s),
            "archetype": archetype,
        })
    return results


def prompt_echo(slot: int) -> Echo:
    """Interactive CLI prompt to collect one echo's stats from the user."""
    print(f"\n  Echo slot {slot}")
    print(f"  Valid stats: {', '.join(VALID_STATS)}")
    name = input("  Echo name (optional): ").strip()
    main = input("  Main stat: ").strip()

    substats: list[EchoSubstat] = []
    print("  Enter substats (leave name blank to finish, max 5):")
    for i in range(5):
        stat = input(f"    Substat {i+1} name: ").strip()
        if not stat:
            break
        try:
            value = float(input(f"    {stat} value: ").strip())
        except ValueError:
            value = 0.0
        substats.append(EchoSubstat(stat=stat, value=value))

    return Echo(slot=slot, main_stat=main, substats=substats, name=name)
