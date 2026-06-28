"""
WutheringWavesOpti — Discord Bot
Run with: python bot.py
"""

import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# This bot is slash-command-only, so the privileged message-content intent
# isn't needed. Quiet discord.py's warning about it being absent (ERROR+ still
# logs so real problems aren't hidden).
logging.getLogger("discord.ext.commands.bot").setLevel(logging.ERROR)

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in .env file. See README for setup instructions.")

intents = discord.Intents.default()

INITIAL_EXTENSIONS = ("cogs.account", "cogs.convene", "cogs.echoes", "cogs.builds")


class WuWaBot(commands.Bot):
    async def setup_hook(self):
        # Runs once, before the gateway connects — the correct place to load
        # cogs and sync. (Doing this in on_ready re-runs on every reconnect and
        # raises ExtensionAlreadyLoaded.)
        for ext in INITIAL_EXTENSIONS:
            await self.load_extension(ext)
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} global command(s)")


bot = WuWaBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}  |  in {len(bot.guilds)} guild(s)")


@bot.tree.command(name="help", description="Show all WuWa Opti commands.")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✦ WuWa Opti — Commands",
        description="Wuthering Waves account optimizer for Discord.",
        color=0xEAB820
    )
    embed.add_field(
        name="/link `url`",
        value="Link your WW account. Paste your convene URL from the game's Convene Records screen.",
        inline=False
    )
    embed.add_field(
        name="/unlink",
        value="Remove your linked account.",
        inline=False
    )
    embed.add_field(
        name="/convene",
        value="View your pull history and pity counters. Toggle banners with buttons.",
        inline=False
    )
    embed.add_field(
        name="/echoes `resonator`",
        value="Score your echo build. Opens a form — enter each echo's main stat and substats.",
        inline=False
    )
    embed.add_field(
        name="/stats",
        value="Show all valid stat names for echo input.",
        inline=False
    )
    embed.add_field(
        name="/build `resonator`",
        value="Show the optimal echo sets, main stats, and substat priority for a resonator. Links to Prydwen.gg for the full guide.",
        inline=False
    )
    embed.set_footer(text="Your credentials are stored privately and never shared.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.run(TOKEN)
