"""
WutheringWavesOpti — Discord Bot
Run with: python bot.py
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in .env file. See README for setup instructions.")

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.load_extension("cogs.account")
    await bot.load_extension("cogs.convene")
    await bot.load_extension("cogs.echoes")
    await bot.load_extension("cogs.builds")
    synced = await bot.tree.sync()
    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)
    print(f"Logged in as {bot.user}  |  {len(synced)} global commands synced to {len(bot.guilds)} guild(s)")


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
