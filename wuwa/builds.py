"""
Static build database sourced from prydwen.gg.
Used by /build command. Update this file as the meta shifts.
"""

ALL_RESONATORS = [
    "Aalto", "Aemeath", "Augusta", "Baizhi", "Brant", "Buling",
    "Calcharo", "Camellya", "Cantarella", "Carlotta", "Cartethyia",
    "Changli", "Chisa", "Chixia", "Ciaccona", "Danjin", "Denia",
    "Encore", "Galbrena", "Hiyuki", "Iuno", "Jianxin", "Jinhsi", "Jiyan",
    "Lingyang", "Lucilla", "Lucy", "Lumi", "Lupa", "Luuk Herssen",
    "Lynae", "Mornye", "Mortefi", "Phoebe", "Phrolova", "Qiuyuan",
    "Rebecca", "Roccia", "Rover (Aero)", "Rover (Havoc)", "Rover (Spectro)",
    "Sanhua", "Sigrika", "Taoqi", "The Shorekeeper", "Verina",
    "Xiangli Yao", "Yangyang", "Yuanwu", "Zani",
]

# slug used in prydwen URLs (lowercase, spaces→hyphens, parens stripped)
def prydwen_slug(name: str) -> str:
    import re
    s = name.lower()
    s = re.sub(r"[()]+", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s


def prydwen_url(name: str) -> str:
    return f"https://www.prydwen.gg/wuthering-waves/characters/{prydwen_slug(name)}"


# Build data: echo_sets, main_stats per slot, priority substats, notes
# Source: prydwen.gg — June 2026
BUILDS: dict[str, dict] = {
    "Jiyan": {
        "role": "Main DPS",
        "element": "Aero",
        "weapon": "Verdant Summit",
        "echo_sets": ["Sierra Gale (5pc)", "Sierra Gale (4pc) + Void Thunder (1pc)"],
        "echo_mains": {
            "4-cost": "CRIT Rate / CRIT DMG",
            "3-cost": "ATK%",
            "3-cost-alt": "Aero DMG%",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Run CRIT Rate/DMG on the 4-cost (Nightmare: Feilian Beringal) — his Aero DMG% comes from the Sierra Gale set + Heavy ATK forte, so the 4-cost is better spent on crit. Aim for 70%+ Crit Rate, then stack Energy Regen for ult uptime.",
        "patch": "3.2",
    },
    "Carlotta": {
        "role": "Main DPS",
        "element": "Glacio",
        "weapon": "Rime-Draped Sprouts",
        "echo_sets": ["Eternal Radiance (5pc)"],
        "echo_mains": {
            "4-cost": "Glacio DMG%",
            "3-cost": "CRIT Rate",
            "3-cost-alt": "ATK%",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT DMG", "CRIT Rate", "ATK%", "Energy Regen"],
        "notes": "Prioritise CRIT DMG after hitting 70% Crit Rate.",
        "patch": "2.1",
    },
    "Changli": {
        "role": "Main DPS / Flex",
        "element": "Fusion",
        "weapon": "Blazing Brilliance",
        "echo_sets": ["Molten Rift (5pc)"],
        "echo_mains": {
            "4-cost": "Fusion DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "High energy cost — prioritise Energy Regen as secondary substat.",
        "patch": "1.3",
    },
    "Camellya": {
        "role": "Main DPS",
        "element": "Havoc",
        "weapon": "Emerald of Genesis",
        "echo_sets": ["Sun-sinking Eclipse (5pc)"],
        "echo_mains": {
            "4-cost": "Havoc DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Excellent off-field damage during petal phase.",
        "patch": "2.0",
    },
    "Jinhsi": {
        "role": "Main DPS",
        "element": "Spectro",
        "weapon": "Ages of Harvest",
        "echo_sets": ["Celestial Light (5pc)"],
        "echo_mains": {
            "4-cost": "Spectro DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT DMG", "CRIT Rate", "ATK%", "Energy Regen"],
        "notes": "Stack Incandescence before using ult for maximum damage.",
        "patch": "1.3",
    },
    "Xiangli Yao": {
        "role": "Main DPS",
        "element": "Electro",
        "weapon": "Lustrous Razor",
        "echo_sets": ["Void Thunder (5pc)"],
        "echo_mains": {
            "4-cost": "Electro DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Rotation-heavy; Energy Regen crucial for consistent ult uptime.",
        "patch": "2.0",
    },
    "Phoebe": {
        "role": "Main DPS",
        "element": "Spectro",
        "weapon": "Stringmaster",
        "echo_sets": ["Celestial Light (5pc)"],
        "echo_mains": {
            "4-cost": "Spectro DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT DMG", "CRIT Rate", "ATK%", "Energy Regen"],
        "notes": "Snapshot build; buff before committing to skill rotation.",
        "patch": "2.2",
    },
    "Cantarella": {
        "role": "Sub-DPS / Support",
        "element": "Havoc",
        "weapon": "Variation",
        "echo_sets": ["Sun-sinking Eclipse (5pc)", "Midnight Veil (5pc)"],
        "echo_mains": {
            "4-cost": "Havoc DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Hybrid support/DPS. Prioritise Energy Regen for consistent ult.",
        "patch": "2.2",
    },
    "Calcharo": {
        "role": "Main DPS",
        "element": "Electro",
        "weapon": "Lustrous Razor",
        "echo_sets": ["Void Thunder (5pc)"],
        "echo_mains": {
            "4-cost": "Electro DMG%",
            "3-cost": "CRIT Rate",
            "3-cost-alt": "ATK%",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT DMG", "CRIT Rate", "ATK%", "Energy Regen"],
        "notes": "Strong burst window; save ult for max stack usage.",
        "patch": "1.0",
    },
    "Encore": {
        "role": "Main DPS",
        "element": "Fusion",
        "weapon": "Cosmic Ripples",
        "echo_sets": ["Molten Rift (5pc)"],
        "echo_mains": {
            "4-cost": "Fusion DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Spend time in sheep/wolf form for maximum skill uptime.",
        "patch": "1.0",
    },
    "Danjin": {
        "role": "Main DPS",
        "element": "Havoc",
        "weapon": "Emerald of Genesis",
        "echo_sets": ["Sun-sinking Eclipse (5pc)"],
        "echo_mains": {
            "4-cost": "Havoc DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Flat ATK"],
        "notes": "HP drain mechanic — don't over-stack HP. Focus raw CRIT stats.",
        "patch": "1.0",
    },
    "Lingyang": {
        "role": "Main DPS",
        "element": "Glacio",
        "weapon": "Abyss Surges",
        "echo_sets": ["Freezing Frost (5pc)"],
        "echo_mains": {
            "4-cost": "Glacio DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Airborne DPS — use ult then launch combos mid-air.",
        "patch": "1.0",
    },
    "Sanhua": {
        "role": "Sub-DPS / Support",
        "element": "Glacio",
        "weapon": "Emerald of Genesis",
        "echo_sets": ["Freezing Frost (5pc)"],
        "echo_mains": {
            "4-cost": "Glacio DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Fast rotation support; swap off quickly after ult.",
        "patch": "1.0",
    },
    "Mortefi": {
        "role": "Sub-DPS / Support",
        "element": "Fusion",
        "weapon": "Variation",
        "echo_sets": ["Molten Rift (5pc)"],
        "echo_mains": {
            "4-cost": "Fusion DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Off-field amplifier; pairs best with heavy attack focused main DPS.",
        "patch": "1.0",
    },
    "Verina": {
        "role": "Support / Healer",
        "element": "Spectro",
        "weapon": "Variation",
        "echo_sets": ["Rejuvenating Glow (5pc)"],
        "echo_mains": {
            "4-cost": "Healing Bonus%",
            "3-cost": "HP%",
            "3-cost-alt": "ATK%",
            "1-cost": "HP%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["Energy Regen", "HP%", "ATK%", "CRIT Rate"],
        "notes": "Universal buffer; ult gives all-element DMG bonus to team.",
        "patch": "1.0",
    },
    "The Shorekeeper": {
        "role": "Support / Healer",
        "element": "Spectro",
        "weapon": "Variation",
        "echo_sets": ["Rejuvenating Glow (5pc)"],
        "echo_mains": {
            "4-cost": "Healing Bonus%",
            "3-cost": "HP%",
            "3-cost-alt": "Energy Regen",
            "1-cost": "HP%",
            "1-cost-2": "HP%",
        },
        "substats": ["Energy Regen", "HP%", "ATK%", "CRIT Rate"],
        "notes": "Best healer in game. Stack Energy Regen for ult uptime.",
        "patch": "1.3",
    },
    "Baizhi": {
        "role": "Support / Healer",
        "element": "Glacio",
        "weapon": "Variation",
        "echo_sets": ["Rejuvenating Glow (5pc)"],
        "echo_mains": {
            "4-cost": "Healing Bonus%",
            "3-cost": "HP%",
            "3-cost-alt": "Energy Regen",
            "1-cost": "HP%",
            "1-cost-2": "HP%",
        },
        "substats": ["Energy Regen", "HP%", "ATK%", "CRIT Rate"],
        "notes": "F2P healer option. Prioritise Energy Regen first.",
        "patch": "1.0",
    },
    "Rover (Havoc)": {
        "role": "Main DPS",
        "element": "Havoc",
        "weapon": "Emerald of Genesis",
        "echo_sets": ["Sun-sinking Eclipse (5pc)"],
        "echo_mains": {
            "4-cost": "Havoc DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Strong free unit. Forte circuit charges quickly in combat.",
        "patch": "1.1",
    },
    "Rover (Spectro)": {
        "role": "Main DPS",
        "element": "Spectro",
        "weapon": "Emerald of Genesis",
        "echo_sets": ["Celestial Light (5pc)"],
        "echo_mains": {
            "4-cost": "Spectro DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Spectro resonance is powerful — pair with Verina or Shorekeeper.",
        "patch": "1.0",
    },
    "Roccia": {
        "role": "Sub-DPS / Support",
        "element": "Havoc",
        "weapon": "Variation",
        "echo_sets": ["Sun-sinking Eclipse (5pc)", "Midnight Veil (5pc)"],
        "echo_mains": {
            "4-cost": "Havoc DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Provides ATK buff and off-field Havoc damage.",
        "patch": "2.0",
    },
    "Brant": {
        "role": "Main DPS",
        "element": "Fusion",
        "weapon": "Blazing Brilliance",
        "echo_sets": ["Molten Rift (5pc)"],
        "echo_mains": {
            "4-cost": "Fusion DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Airborne-focused DPS — maintain air time during ult window.",
        "patch": "2.1",
    },
    "Zani": {
        "role": "Sub-DPS / Support",
        "element": "Electro",
        "weapon": "Variation",
        "echo_sets": ["Void Thunder (5pc)"],
        "echo_mains": {
            "4-cost": "Electro DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Stacks Electro debuffs off-field for main DPS to exploit.",
        "patch": "2.2",
    },
    "Aalto": {
        "role": "Sub-DPS / Support",
        "element": "Aero",
        "weapon": "Variation",
        "echo_sets": ["Sierra Gale (5pc)"],
        "echo_mains": {
            "4-cost": "Aero DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "Mist Avatar provides Aero DMG bonus to active resonator.",
        "patch": "1.0",
    },
    "Chixia": {
        "role": "Main DPS",
        "element": "Fusion",
        "weapon": "Cosmic Ripples",
        "echo_sets": ["Molten Rift (5pc)"],
        "echo_mains": {
            "4-cost": "Fusion DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "CRIT Rate",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Energy Regen"],
        "notes": "F2P DPS. DOOM mode is her main damage window.",
        "patch": "1.0",
    },
    "Yangyang": {
        "role": "Support / Sub-DPS",
        "element": "Aero",
        "weapon": "Variation",
        "echo_sets": ["Sierra Gale (5pc)"],
        "echo_mains": {
            "4-cost": "Aero DMG%",
            "3-cost": "ATK%",
            "3-cost-alt": "Energy Regen",
            "1-cost": "ATK%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["Energy Regen", "CRIT Rate", "CRIT DMG", "ATK%"],
        "notes": "Useful for grouping/gathering enemies with ult.",
        "patch": "1.0",
    },
    "Taoqi": {
        "role": "Tank / Support",
        "element": "Havoc",
        "weapon": "Variation",
        "echo_sets": ["Midnight Veil (5pc)"],
        "echo_mains": {
            "4-cost": "Havoc DMG%",
            "3-cost": "DEF%",
            "3-cost-alt": "HP%",
            "1-cost": "DEF%",
            "1-cost-2": "Energy Regen",
        },
        "substats": ["DEF%", "HP%", "Energy Regen", "CRIT Rate"],
        "notes": "Shield scales with DEF. Focus DEF% main stats on all slots.",
        "patch": "1.0",
    },
    "Jianxin": {
        "role": "Tank / Support",
        "element": "Aero",
        "weapon": "Variation",
        "echo_sets": ["Sierra Gale (5pc)"],
        "echo_mains": {
            "4-cost": "HP%",
            "3-cost": "HP%",
            "3-cost-alt": "Energy Regen",
            "1-cost": "HP%",
            "1-cost-2": "HP%",
        },
        "substats": ["Energy Regen", "HP%", "DEF%", "CRIT Rate"],
        "notes": "Shield and pull utility. Prioritise HP% for stronger shields.",
        "patch": "1.0",
    },
    "Lucilla": {
        "role": "Main DPS / Support",
        "element": "Glacio",
        "weapon": "Freeze Frame",
        "echo_sets": ["Wishes of Quiet Snowfall (5pc) — Glacio Chafe team", "Dream of the Lost (5pc) — Phrolova team"],
        "echo_mains": {
            "4-cost": "CRIT Rate / CRIT DMG",
            "3-cost": "Glacio DMG%",
            "3-cost-alt": "Glacio DMG%",
            "1-cost": "ATK%",
            "1-cost-2": "ATK%",
        },
        "substats": ["CRIT Rate", "CRIT DMG", "ATK%", "Flat ATK"],
        "notes": "Echo set depends on team: Wishes of Quiet Snowfall with Glacio Chafe, Dream of the Lost with Phrolova. In Echo mode prioritise ATK over Basic DMG%.",
        "patch": "3.x",
    },
}


# ---------------------------------------------------------------------------
# Skill (Forte) leveling priority — the order to pour upgrade mats into.
# The five nodes are: Basic Attack, Resonance Skill, Resonance Liberation,
# Forte Circuit, Intro Skill. Listed best-first.
# Source: game8.co / community guides — cross-reference in-game for your patch.
# ---------------------------------------------------------------------------
SKILL_PRIORITY: dict[str, str] = {
    # Jiyan — verified via game8: Qingloong Mode scales off Liberation first,
    # then Forte Circuit and Resonance Skill catch up.
    "Jiyan":          "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Carlotta":       "Forte Circuit → Resonance Liberation → Resonance Skill → Basic Attack → Intro Skill",
    "Changli":        "Resonance Skill → Resonance Liberation → Forte Circuit → Basic Attack → Intro Skill",
    "Camellya":       "Forte Circuit → Resonance Liberation → Resonance Skill → Basic Attack → Intro Skill",
    "Jinhsi":         "Resonance Liberation → Forte Circuit → Resonance Skill → Intro Skill → Basic Attack",
    "Xiangli Yao":    "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Phoebe":         "Resonance Skill → Resonance Liberation → Forte Circuit → Basic Attack → Intro Skill",
    "Cantarella":     "Resonance Skill → Resonance Liberation → Forte Circuit → Basic Attack → Intro Skill",
    "Calcharo":       "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Encore":         "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Danjin":         "Resonance Skill → Resonance Liberation → Forte Circuit → Basic Attack → Intro Skill",
    "Lingyang":       "Resonance Skill → Forte Circuit → Resonance Liberation → Basic Attack → Intro Skill",
    "Sanhua":         "Resonance Skill → Basic Attack → Resonance Liberation → Forte Circuit → Intro Skill",
    "Mortefi":        "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Verina":         "Resonance Liberation → Resonance Skill → Forte Circuit → Intro Skill → Basic Attack  (low priority — buffs barely scale with level)",
    "The Shorekeeper": "Resonance Skill → Resonance Liberation → Forte Circuit → Intro Skill → Basic Attack",
    "Baizhi":         "Resonance Skill → Resonance Liberation → Forte Circuit → Intro Skill → Basic Attack  (low priority)",
    "Rover (Havoc)":  "Forte Circuit → Resonance Liberation → Resonance Skill → Basic Attack → Intro Skill",
    "Rover (Spectro)": "Resonance Skill → Resonance Liberation → Forte Circuit → Basic Attack → Intro Skill",
    "Roccia":         "Resonance Skill → Forte Circuit → Resonance Liberation → Basic Attack → Intro Skill",
    "Brant":          "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Zani":           "Forte Circuit → Resonance Skill → Resonance Liberation → Basic Attack → Intro Skill",
    "Aalto":          "Resonance Skill → Resonance Liberation → Forte Circuit → Basic Attack → Intro Skill  (low priority — buffer)",
    "Chixia":         "Resonance Liberation → Forte Circuit → Resonance Skill → Basic Attack → Intro Skill",
    "Yangyang":       "Resonance Liberation → Resonance Skill → Forte Circuit → Intro Skill → Basic Attack  (low priority)",
    "Taoqi":          "Resonance Skill → Forte Circuit → Resonance Liberation → Basic Attack → Intro Skill  (DEF-scaling shielder)",
    "Jianxin":        "Resonance Skill → Resonance Liberation → Forte Circuit → Intro Skill → Basic Attack",
    "Lucilla":        "Resonance Skill → Forte Circuit → Resonance Liberation → Basic Attack → Intro Skill",
}

# Recommended main echo (the 4-cost Echo that anchors the build).
MAIN_ECHO: dict[str, str] = {
    "Jiyan":          "Nightmare: Feilian Beringal",   # verified via game8
    "Xiangli Yao":    "Nightmare: Tempest Mephis",
    "Calcharo":       "Nightmare: Thundering Mephis",
}

# ---------------------------------------------------------------------------
# Full-build cost: level 1→90 + all five Forte skills to level 10.
# In Wuthering Waves these totals do NOT scale with rarity — a 4★ and a 5★
# cost the same Shell Credits / EXP and the same material *tier counts*; only
# the named items differ (see per-character MATERIALS below). Weapon excluded.
# Figures are the standardized community totals (game8 / wuwa.uk planner).
# ---------------------------------------------------------------------------
FULL_BUILD_COST = {
    "shell_credits": 2_200_000,      # ~170,000 ascension + ~2,030,000 forte
    "character_exp": "≈1,786,500 EXP (Resonance Potions)",
    "ascension_counts": "Specialty ×60 · Boss echo mat ×46 · Enemy core ×4/12/12/4 (LF/MF/HF/FF)",
    "forte_counts": "Forgery mat & enemy core (all four tiers) · Weekly boss mat ×23",
}

# Named materials per resonator (the items unique to each character).
# slots: specialty, boss (overworld ascension echo), enemy_core,
#        forgery (forte/talent mat), weekly_boss.
# Verified entries are marked; others are best-effort — verify in-game.
MATERIALS: dict[str, dict] = {
    "Jiyan": {  # verified via game8.co
        "specialty": "Pecok Flower",
        "boss": "Roaring Rock Fist",
        "enemy_core": "Howler Core",
        "forgery": "Waveworn Residue",
        "weekly_boss": "Monument Bell",
    },
    "Xiangli Yao": {  # verified via game8.co
        "specialty": "Violet Coral",
        "boss": "Hidden Thunder Tacet Core",
        "enemy_core": "Whisperin Core",
        "forgery": "Cadence Seed",
        "weekly_boss": "Unending Destruction",
    },
}


def get_build(name: str) -> dict | None:
    data = BUILDS.get(name)
    if data is None:
        return None
    enriched = dict(data)
    enriched["skill_priority"] = SKILL_PRIORITY.get(name)
    enriched["main_echo"] = MAIN_ECHO.get(name)
    enriched["materials"] = MATERIALS.get(name)
    enriched["full_build_cost"] = FULL_BUILD_COST
    return enriched


def get_all_names() -> list[str]:
    return sorted(ALL_RESONATORS)
