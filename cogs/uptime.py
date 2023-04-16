#!/usr/bin/env python3
# Discord bot: cogs/uptime.py

from discord.ext import commands
from discord import app_commands
from process_uptime import getuptime

class UptimeCog(commands.Cog):
    """Uptime command."""

    def __init__(self, bot):
        self.bot = bot
        self.sessions: set[int] = set()

    @app_commands.command(name="uptime", description="Prints the bot uptime")
    async def uptime(self, ctx) -> None:
        """Prints the bot uptime."""
        try:
            uptime = getuptime()
            uptimeDays = int(uptime // 60 // 60 // 24)
            uptimeHours = (uptime // 60 // 60) % 24
            uptimeMinutes = (uptime // 60) % 60
            uptimeSeconds = uptime % 60
            await ctx.response.send_message("Uptime: " + str(uptimeDays) + "d " + str(uptimeHours) + "h " + str(uptimeMinutes) + "m " + str(uptimeSeconds) + "s. \N{OK HAND SIGN}")
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}')

async def setup(bot):
    await bot.add_cog(UptimeCog(bot))