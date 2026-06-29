import discord
from discord import app_commands
from discord.ext import commands

from wuwa.echo import score_build, build_suggestions, RESONATOR_ARCHETYPES, VALID_STATS, Echo, EchoSubstat, grade

GOLD        = 0xEAB820
GRADE_COLOR = {"S": 0x3EC98A, "A": 0xEAB820, "B": 0xFF8C1A, "C": 0x7A8A9E, "D": 0xD94040}

# Display names for the stat-scaling buckets. This is the *scoring profile*
# (how substats are weighted), NOT a battlefield role — a sub-DPS can still
# scale on crit and sit in "Crit DPS".
SCALING_LABELS = {
    "crit_dps": "Crit DPS", "atk_dps": "ATK DPS", "support": "Support",
    "tank": "Tank", "hp_dps": "HP DPS", "def_support": "DEF Support",
}

# Echo slot → cost (WuWa: slot 1 = 4-cost, 2–3 = 3-cost, 4–5 = 1-cost)
SLOT_COST = {1: "4-cost", 2: "3-cost", 3: "3-cost", 4: "1-cost", 5: "1-cost"}

RESONATORS = sorted(RESONATOR_ARCHETYPES.keys())


def _result_embed(echoes: list[Echo], resonator: str) -> discord.Embed:
    results = score_build(echoes, resonator)
    avg      = sum(r["score"] for r in results) / len(results) if results else 0
    og       = grade(avg)
    raw_arch = results[0]["archetype"] if results else ""
    arch     = SCALING_LABELS.get(raw_arch, raw_arch.replace("_", " ").title() or "—")

    embed = discord.Embed(
        title=f"◈ Echo Build — {resonator}",
        description=f"Scaling profile: **{arch}**  *(how substats are weighted, not role)*",
        color=GRADE_COLOR.get(og, GOLD),
    )
    for r in results:
        g    = r["grade"]
        bar  = "█" * int(r["score"] / 10) + "░" * (10 - int(r["score"] / 10))
        embed.add_field(
            name=f"Echo {r['slot']}  {r['name']}",
            value=f"`{bar}` **{r['score']}/100** — Grade **{g}**\nMain: {r['main_stat']}",
            inline=False,
        )
    embed.add_field(name="Overall", value=f"Score: **{avg:.1f}/100** — Grade **{og}**", inline=False)

    tips = build_suggestions(echoes, resonator)
    embed.add_field(name="🛠 How to optimize", value="\n".join(f"• {t}" for t in tips)[:1024], inline=False)
    embed.set_footer(text=f"Substats weighted for {arch} scaling · Higher = better")
    return embed


class MainStatSelect(discord.ui.Select):
    def __init__(self, current: str | None):
        options = [discord.SelectOption(label=s, value=s, default=(s == current)) for s in VALID_STATS]
        super().__init__(placeholder="Main stat…", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        self.view.current()["main"] = self.values[0]
        self.view.render()
        await interaction.response.edit_message(embed=self.view.embed(), view=self.view)


class SubStatSelect(discord.ui.Select):
    def __init__(self, current: list[str]):
        options = [discord.SelectOption(label=s, value=s, default=(s in current)) for s in VALID_STATS]
        super().__init__(placeholder="Substats (pick up to 5)…", min_values=0, max_values=5, options=options, row=1)

    async def callback(self, interaction: discord.Interaction):
        self.view.current()["subs"] = list(self.values)
        self.view.render()
        await interaction.response.edit_message(embed=self.view.embed(), view=self.view)


class NavButton(discord.ui.Button):
    def __init__(self, label: str, delta: int, disabled: bool):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, row=2, disabled=disabled)
        self.delta = delta

    async def callback(self, interaction: discord.Interaction):
        self.view.slot = max(1, min(5, self.view.slot + self.delta))
        self.view.render()
        await interaction.response.edit_message(embed=self.view.embed(), view=self.view)


class ScoreButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✅ Score Build", style=discord.ButtonStyle.success, row=2)

    async def callback(self, interaction: discord.Interaction):
        echoes = self.view.build_echoes()
        embed  = _result_embed(echoes, self.view.resonator)
        self.view.stop()
        await interaction.response.edit_message(embed=embed, view=None)


class EchoBuilderView(discord.ui.View):
    """Dropdown-driven echo builder. State is per-slot; values are auto-handled
    (scoring is by stat presence, so the user never types numbers)."""

    def __init__(self, resonator: str, author_id: int):
        super().__init__(timeout=300)
        self.resonator = resonator
        self.author_id = author_id
        self.slot      = 1
        self.data      = {i: {"main": None, "subs": []} for i in range(1, 6)}
        self.render()

    def current(self) -> dict:
        return self.data[self.slot]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This isn't your echo builder — run `/echoes` yourself.", ephemeral=True
            )
            return False
        return True

    def render(self):
        self.clear_items()
        cur = self.current()
        self.add_item(MainStatSelect(cur["main"]))
        self.add_item(SubStatSelect(cur["subs"]))
        self.add_item(NavButton("◀ Prev", -1, disabled=(self.slot == 1)))
        self.add_item(NavButton("Next ▶", +1, disabled=(self.slot == 5)))
        self.add_item(ScoreButton())

    def embed(self) -> discord.Embed:
        e = discord.Embed(
            title=f"◈ Build {self.resonator}'s Echoes",
            description=(
                f"Editing **Echo {self.slot}/5**  ·  {SLOT_COST[self.slot]}\n"
                "Pick the main stat and substats from the dropdowns, use **◀ / ▶** to move "
                "between echoes, then **Score Build**."
            ),
            color=GOLD,
        )
        for i in range(1, 6):
            d      = self.data[i]
            main   = d["main"] or "—"
            subs   = ", ".join(d["subs"]) if d["subs"] else "—"
            marker = "▶ " if i == self.slot else ""
            e.add_field(name=f"{marker}Echo {i} · {SLOT_COST[i]}", value=f"Main: **{main}**\nSubs: {subs}", inline=False)
        e.set_footer(text="Values are auto-handled — scored by stat presence, no numbers to type.")
        return e

    def build_echoes(self) -> list[Echo]:
        echoes = []
        for i in range(1, 6):
            d = self.data[i]
            echoes.append(Echo(
                slot=i,
                main_stat=d["main"] or "ATK%",
                substats=[EchoSubstat(stat=s, value=0.0) for s in d["subs"]],
                name=f"Echo {i}",
            ))
        return echoes


class Echoes(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def resonator_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=r, value=r)
            for r in RESONATORS if current.lower() in r.lower()
        ][:25]

    @app_commands.command(name="echoes", description="Score your echo build for a resonator (dropdown builder).")
    @app_commands.describe(resonator="Start typing a resonator name")
    @app_commands.autocomplete(resonator=resonator_autocomplete)
    async def echoes(self, interaction: discord.Interaction, resonator: str):
        if resonator not in RESONATOR_ARCHETYPES:
            await interaction.response.send_message(
                f"Unknown resonator `{resonator}`. Use `/echoes` and pick from the dropdown.",
                ephemeral=True,
            )
            return
        view = EchoBuilderView(resonator, interaction.user.id)
        await interaction.response.send_message(embed=view.embed(), view=view, ephemeral=True)

    @app_commands.command(name="stats", description="Show valid stat names for echo input.")
    async def stats(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Valid Echo Stats", color=GOLD)
        embed.description = "\n".join(f"• `{s}`" for s in VALID_STATS)
        embed.set_footer(text="These are the options in the /echoes dropdowns.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot): await bot.add_cog(Echoes(bot))
