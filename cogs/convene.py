import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from wuwa.convene import (
    fetch_all, pity_stats, POOL_TYPES, COLLAB_POOLS, collab_active, available_pools,
)
from wuwa.store import get_creds, get_cache, set_cache, load_cache_results

BASE_POOL_IDS = [1, 2, 3, 4]
STAR5 = 0xFFD700
STAR4 = 0xB966E7
GOLD  = 0xEAB820


def _selectable_pools() -> dict[int, str]:
    """Banners shown as toggles: the 4 standard banners, plus collab banners
    while the collaboration event is live."""
    pools = {pid: POOL_TYPES[pid] for pid in BASE_POOL_IDS}
    if collab_active():
        pools.update(COLLAB_POOLS)
    return pools


def _pool_embed(pool_id: int, records: list) -> discord.Embed:
    s = pity_stats(records)
    name = available_pools().get(pool_id, f"Pool {pool_id}")

    embed = discord.Embed(title=f"✦ {name}", color=GOLD)
    embed.add_field(name="Total Pulls",  value=str(s["total_pulls"]),    inline=True)
    embed.add_field(name="5★ Pity",      value=f"**{s['current_pity_5']}**", inline=True)
    embed.add_field(name="4★ Pity",      value=str(s["current_pity_4"]), inline=True)
    embed.add_field(name="5★ Count",     value=str(s["total_5star"]),    inline=True)
    embed.add_field(name="5★ Rate",      value=f"{s['rate_5star']}%",    inline=True)
    embed.add_field(name="​",       value="​",                  inline=True)

    # Pity = how many pulls it took to land each 5★ (pulls since the previous
    # 5★, inclusive of the winning pull). records is newest-first, so walk
    # oldest→newest, counting the streak and resetting it on each 5★.
    pity_at: dict[int, int] = {}
    streak = 0
    for r in reversed(records):
        streak += 1
        if r.rarity == 5:
            pity_at[id(r)] = streak
            streak = 0

    recent_5 = [r for r in records if r.rarity == 5][:5]
    if recent_5:
        lines = "\n".join(
            f"★★★★★ **{r.name}** — pity {pity_at.get(id(r), '?')}" for r in recent_5
        )
        embed.add_field(name="Recent 5★", value=lines, inline=False)

    recent = records[:15]
    lines = []
    for r in recent:
        star = "★" * r.rarity + "☆" * (5 - r.rarity)
        lines.append(f"`{star}` {r.name} · {r.type} · {r.pull_time[:10]}")
    if lines:
        embed.add_field(name="Recent Pulls", value="\n".join(lines), inline=False)

    return embed


class ConvenePoolView(discord.ui.View):
    def __init__(self, creds: dict, user_id: int):
        super().__init__(timeout=120)
        self.creds   = creds
        self.user_id = user_id
        self.pools   = _selectable_pools()
        self.selected: set[int] = set(self.pools)
        self._add_buttons()

    def _add_buttons(self):
        self.clear_items()
        for i, (pid, name) in enumerate(self.pools.items()):
            active = pid in self.selected
            self.add_item(PoolToggle(pid, name, active, row=i // 5))
        action_row = (len(self.pools) - 1) // 5 + 1
        self.add_item(FetchButton(row=action_row))
        self.add_item(RefreshButton(row=action_row))

    def toggle(self, pid: int):
        if pid in self.selected: self.selected.discard(pid)
        else:                    self.selected.add(pid)
        self._add_buttons()


class PoolToggle(discord.ui.Button):
    def __init__(self, pid: int, name: str, active: bool, row: int = 0):
        super().__init__(
            label=name,
            style=discord.ButtonStyle.primary if active else discord.ButtonStyle.secondary,
            custom_id=f"pool_{pid}",
            row=row,
        )
        self.pid = pid

    async def callback(self, interaction: discord.Interaction):
        self.view.toggle(self.pid)
        await interaction.response.edit_message(view=self.view)


class FetchButton(discord.ui.Button):
    def __init__(self, row: int = 2):
        super().__init__(label="⬇  Fetch History", style=discord.ButtonStyle.success, row=row)

    async def callback(self, interaction: discord.Interaction):
        if not self.view.selected:
            await interaction.response.send_message("Select at least one banner first.", ephemeral=True)
            return

        await interaction.response.defer()
        creds   = self.view.creds
        user_id = self.view.user_id
        pools   = list(self.view.selected)

        cached = get_cache(user_id, pools)
        if cached:
            results = load_cache_results(user_id)
            source  = "cached"
        else:
            loop    = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, lambda: fetch_all(creds, pools, force=True)[0])
            set_cache(user_id, results)
            source  = "live"

        embeds = [_pool_embed(pid, records)
                  for pid, records in sorted(results.items()) if records]
        if not embeds:
            await interaction.followup.send("No records found for the selected banners.", ephemeral=True)
            return

        embeds[0].set_footer(text=f"Source: {source} · {len(pools)} banner(s) fetched")
        for embed in embeds:
            await interaction.followup.send(embed=embed)


class RefreshButton(discord.ui.Button):
    def __init__(self, row: int = 2):
        super().__init__(label="↺  Force Refresh", style=discord.ButtonStyle.secondary, row=row)

    async def callback(self, interaction: discord.Interaction):
        if not self.view.selected:
            await interaction.response.send_message("Select at least one banner first.", ephemeral=True)
            return

        await interaction.response.defer()
        creds   = self.view.creds
        user_id = self.view.user_id
        pools   = list(self.view.selected)

        loop    = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, lambda: fetch_all(creds, pools, force=True)[0])
        set_cache(user_id, results)

        embeds = [_pool_embed(pid, records)
                  for pid, records in sorted(results.items()) if records]
        if embeds:
            embeds[0].set_footer(text="Source: live (force refresh)")
            for embed in embeds:
                await interaction.followup.send(embed=embed)


class Convene(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="convene", description="View your Wuthering Waves convene history and pity.")
    async def convene(self, interaction: discord.Interaction):
        creds = get_creds(interaction.user.id)
        if not creds:
            await interaction.response.send_message(
                "You haven't linked your account yet. Use `/link` first.", ephemeral=True
            )
            return

        view  = ConvenePoolView(creds, interaction.user.id)
        embed = discord.Embed(
            title="✦ Convene Records",
            description="Toggle banners below then click **Fetch History**.",
            color=GOLD
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot): await bot.add_cog(Convene(bot))
