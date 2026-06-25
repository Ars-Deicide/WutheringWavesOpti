import discord
from discord import app_commands
from discord.ext import commands

from wuwa.log_parser import parse_convene_url
from wuwa.store import get_creds, set_creds


class Account(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="link", description="Link your Wuthering Waves account via your convene URL.")
    @app_commands.describe(url="Paste your convene URL here (from the game's Convene Records screen)")
    async def link(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(ephemeral=True)

        creds = parse_convene_url(url.strip())
        if not creds:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Invalid URL",
                    description=(
                        "Could not parse that URL.\n\n"
                        "**How to get your convene URL:**\n"
                        "1. Open Wuthering Waves\n"
                        "2. Go to **Convene → Convene Records**\n"
                        "3. Log into **wutheringwaves.kurogames.com** in your browser\n"
                        "4. Open Convene Records there, press **F12 → Network**\n"
                        "5. Filter by `query` and copy the request URL"
                    ),
                    color=0xD94040
                ),
                ephemeral=True
            )
            return

        set_creds(interaction.user.id, creds)

        embed = discord.Embed(
            title="✅ Account Linked",
            color=0xEAB820
        )
        embed.add_field(name="Player ID", value=creds["player_id"], inline=True)
        embed.add_field(name="Region",    value=creds["svr_area"].upper(), inline=True)
        embed.add_field(name="Language",  value=creds["lang"].upper(), inline=True)
        embed.set_footer(text="Your credentials are saved privately. Use /convene to fetch your history.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="unlink", description="Remove your linked Wuthering Waves account.")
    async def unlink(self, interaction: discord.Interaction):
        from wuwa.store import _load, _save, USERS_FILE
        data = _load(USERS_FILE)
        uid = str(interaction.user.id)
        if uid in data:
            del data[uid]
            _save(USERS_FILE, data)
            await interaction.response.send_message("✅ Your account has been unlinked.", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have a linked account.", ephemeral=True)


async def setup(bot): await bot.add_cog(Account(bot))
