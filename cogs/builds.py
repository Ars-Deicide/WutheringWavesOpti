import discord
from discord import app_commands
from discord.ext import commands

from wuwa.builds import get_build, get_all_names, prydwen_url

GOLD = 0xEAB820
ELEMENT_COLORS = {
    "Aero":    0x6FCF97,
    "Electro": 0xBB6BD9,
    "Fusion":  0xEB5757,
    "Glacio":  0x56CCF2,
    "Havoc":   0x9B51E0,
    "Spectro": 0xF2C94C,
}

ALL_RESONATORS = get_all_names()


class Builds(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def resonator_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=r, value=r)
            for r in ALL_RESONATORS if current.lower() in r.lower()
        ][:25]

    @app_commands.command(name="build", description="Show the optimal build for a resonator.")
    @app_commands.describe(resonator="Start typing a resonator name")
    @app_commands.autocomplete(resonator=resonator_autocomplete)
    async def build(self, interaction: discord.Interaction, resonator: str):
        data = get_build(resonator)
        url  = prydwen_url(resonator)

        if data is None:
            embed = discord.Embed(
                title=f"◈ {resonator}",
                description=(
                    "No curated build data yet for this resonator.\n"
                    f"[View on Prydwen.gg]({url})"
                ),
                color=GOLD,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        color = ELEMENT_COLORS.get(data.get("element", ""), GOLD)
        embed = discord.Embed(
            title=f"◈ {resonator}  —  {data['role']}",
            url=url,
            color=color,
        )

        # Transparent character art, if an image source is configured.
        if data.get("image"):
            embed.set_image(url=data["image"])

        embed.add_field(
            name="Element / Weapon",
            value=f"{data.get('element', '—')} · {data['weapon']}",
            inline=False,
        )

        sets_str = "\n".join(f"• {s}" for s in data["echo_sets"])
        embed.add_field(name="Echo Sets", value=sets_str, inline=False)

        if data.get("main_echo"):
            embed.add_field(name="Main Echo (4-cost)", value=data["main_echo"], inline=False)

        mains = data["echo_mains"]
        mains_lines = [
            f"4★ (4-cost): **{mains.get('4-cost', '—')}**",
            f"3★ (3-cost): **{mains.get('3-cost', '—')}** / **{mains.get('3-cost-alt', '—')}**",
            f"1★ (1-cost): **{mains.get('1-cost', '—')}** / **{mains.get('1-cost-2', '—')}**",
        ]
        embed.add_field(name="Echo Main Stats", value="\n".join(mains_lines), inline=False)

        substats_str = " > ".join(data["substats"])
        embed.add_field(name="Substat Priority", value=substats_str, inline=False)

        if data.get("skill_priority"):
            embed.add_field(name="Skill Priority (Forte)", value=data["skill_priority"], inline=False)

        cost = data.get("full_build_cost")
        if cost:
            cost_lines = [
                f"**Shell Credits:** ~{cost['shell_credits']:,}",
                f"**Character EXP:** {cost['character_exp']}",
                f"**Ascension:** {cost['ascension_counts']}",
                f"**Forte (all skills):** {cost['forte_counts']}",
            ]
            embed.add_field(name="Full Build Cost (Lv.90 + all skills)", value="\n".join(cost_lines), inline=False)

        mats = data.get("materials")
        if mats:
            mats_lines = [
                f"**Specialty:** {mats['specialty']}",
                f"**Boss (ascension):** {mats['boss']}",
                f"**Enemy core:** {mats['enemy_core']}",
                f"**Forte forgery:** {mats['forgery']}",
                f"**Weekly boss:** {mats['weekly_boss']}",
            ]
            embed.add_field(name="Character Materials", value="\n".join(mats_lines), inline=False)

        if data.get("notes"):
            embed.add_field(name="Notes", value=data["notes"], inline=False)

        mat_note = "" if mats else "  ·  character-specific mats: see in-game"
        embed.set_footer(text=f"Build: prydwen.gg/game8.co  ·  patch {data.get('patch', '?')}  ·  cost totals are standardized{mat_note}")
        await interaction.response.send_message(embed=embed)


async def setup(bot): await bot.add_cog(Builds(bot))
