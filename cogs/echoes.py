import discord
from discord import app_commands
from discord.ext import commands

from wuwa.echo import score_build, build_suggestions, RESONATOR_ARCHETYPES, VALID_STATS, Echo, EchoSubstat, grade

GOLD        = 0xEAB820
GRADE_COLOR = {"S": 0x3EC98A, "A": 0xEAB820, "B": 0xFF8C1A, "C": 0x7A8A9E, "D": 0xD94040}
VALID_SET   = set(VALID_STATS)

# Display names for the stat-scaling buckets. This is the *scoring profile*
# (how substats are weighted), NOT a battlefield role — a sub-DPS can still
# scale on crit and sit in "Crit DPS".
SCALING_LABELS = {
    "crit_dps": "Crit DPS", "atk_dps": "ATK DPS", "support": "Support",
    "tank": "Tank", "hp_dps": "HP DPS", "def_support": "DEF Support",
}


def _parse_echo_field(slot: int, text: str) -> Echo | str:
    """
    Parse one echo field. Format:
      MainStat | Sub1, Sub2, Sub3, Sub4, Sub5
    Returns Echo on success or an error string.
    """
    text = text.strip()
    if not text or text == "-":
        return Echo(slot=slot, main_stat="ATK%", substats=[], name=f"Echo {slot}")

    parts = [p.strip() for p in text.split("|", 1)]
    main  = parts[0].strip()
    if main not in VALID_SET:
        close = [s for s in VALID_STATS if main.lower() in s.lower()]
        hint  = f" (did you mean: {', '.join(close[:3])}?)" if close else ""
        return f"Echo {slot}: unknown main stat **{main}**{hint}"

    substats = []
    if len(parts) > 1:
        for raw in parts[1].split(","):
            s = raw.strip()
            if not s: continue
            if s not in VALID_SET:
                return f"Echo {slot}: unknown substat **{s}**"
            substats.append(EchoSubstat(stat=s, value=0.0))

    return Echo(slot=slot, main_stat=main, substats=substats[:5])


class EchoModal(discord.ui.Modal, title="Echo Build Input"):
    help_text = (
        "Format each slot:  MainStat | Sub1, Sub2, Sub3\n"
        "Example:  ATK% | CRIT Rate, CRIT DMG, ATK%\n"
        "Leave blank to skip a slot.\n\n"
        f"Valid stats: {', '.join(VALID_STATS)}"
    )

    e1 = discord.ui.TextInput(label="Echo 1  (MainStat | Sub1, Sub2, …)", placeholder="ATK% | CRIT Rate, CRIT DMG", required=False)
    e2 = discord.ui.TextInput(label="Echo 2  (MainStat | Sub1, Sub2, …)", placeholder="CRIT Rate | CRIT DMG, ATK%", required=False)
    e3 = discord.ui.TextInput(label="Echo 3  (MainStat | Sub1, Sub2, …)", placeholder="ATK% | CRIT Rate, CRIT DMG", required=False)
    e4 = discord.ui.TextInput(label="Echo 4  (MainStat | Sub1, Sub2, …)", placeholder="Energy Regen | ATK%, CRIT Rate", required=False)
    e5 = discord.ui.TextInput(label="Echo 5  (MainStat | Sub1, Sub2, …)", placeholder="ATK% | CRIT DMG, CRIT Rate", required=False)

    def __init__(self, resonator: str):
        super().__init__()
        self.resonator = resonator

    async def on_submit(self, interaction: discord.Interaction):
        fields  = [self.e1, self.e2, self.e3, self.e4, self.e5]
        echoes  = []
        errors  = []

        for i, field in enumerate(fields, 1):
            result = _parse_echo_field(i, field.value or "")
            if isinstance(result, str):
                errors.append(result)
            else:
                echoes.append(result)

        if errors:
            await interaction.response.send_message(
                "**Input errors:**\n" + "\n".join(f"• {e}" for e in errors),
                ephemeral=True
            )
            return

        results = score_build(echoes, self.resonator)
        avg     = sum(r["score"] for r in results) / len(results) if results else 0
        og      = grade(avg)
        raw_arch = results[0]["archetype"] if results else ""
        arch     = SCALING_LABELS.get(raw_arch, raw_arch.replace("_", " ").title() or "—")

        embed = discord.Embed(
            title=f"◈ Echo Build — {self.resonator}",
            description=f"Scaling profile: **{arch}**  *(how substats are weighted, not role)*",
            color=GRADE_COLOR.get(og, GOLD)
        )

        for r in results:
            g     = r["grade"]
            bar   = "█" * int(r["score"] / 10) + "░" * (10 - int(r["score"] / 10))
            value = f"`{bar}` **{r['score']}/100** — Grade **{g}**\nMain: {r['main_stat']}"
            embed.add_field(name=f"Echo {r['slot']}  {r['name']}", value=value, inline=False)

        embed.add_field(
            name="Overall",
            value=f"Score: **{avg:.1f}/100** — Grade **{og}**",
            inline=False
        )

        tips = build_suggestions(echoes, self.resonator)
        embed.add_field(
            name="🛠 How to optimize",
            value="\n".join(f"• {t}" for t in tips)[:1024],
            inline=False
        )
        embed.set_footer(text=f"Substats weighted for {arch} scaling · Higher = better")
        await interaction.response.send_message(embed=embed)


RESONATORS = sorted(RESONATOR_ARCHETYPES.keys())


class Echoes(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def resonator_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=r, value=r)
            for r in RESONATORS if current.lower() in r.lower()
        ][:25]

    @app_commands.command(name="echoes", description="Score your echo build for a resonator.")
    @app_commands.describe(resonator="Start typing a resonator name")
    @app_commands.autocomplete(resonator=resonator_autocomplete)
    async def echoes(self, interaction: discord.Interaction, resonator: str):
        if resonator not in RESONATOR_ARCHETYPES:
            await interaction.response.send_message(
                f"Unknown resonator `{resonator}`. Use `/echoes` and pick from the dropdown.",
                ephemeral=True
            )
            return
        await interaction.response.send_modal(EchoModal(resonator))

    @app_commands.command(name="stats", description="Show valid stat names for echo input.")
    async def stats(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Valid Echo Stats", color=GOLD)
        embed.description = "\n".join(f"• `{s}`" for s in VALID_STATS)
        embed.set_footer(text="Use these exact names in /echoes input fields.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot): await bot.add_cog(Echoes(bot))
