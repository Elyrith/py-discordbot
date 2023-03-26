#!/usr/bin/env python3
# Discord bot: cogs/uptime.py

from discord.ext import commands
from process_uptime import getuptime

class Uptime(commands.Cog):
    """Uptime command."""

    def __init__(self, bot):
        self.bot = bot
        self.sessions: set[int] = set()

    @commands.command(hidden=False)
    async def uptime(self, ctx):
        """Prints the bot uptime."""
        try:
            uptime = getuptime()
            uptimeDays = int(uptime // 60 // 60 // 24)
            uptimeHours = int(uptime // 60 // 60)
            uptimeMinutes = int((uptime % 3600) // 60)
            uptimeSeconds = uptime % 60
            await ctx.reply("Uptime: " + str(uptimeDays) + "d " + str(uptimeHours) + "h " + str(uptimeMinutes) + "m " + str(uptimeSeconds) + "s. \N{OK HAND SIGN}")
        except commands.ExtensionError as e:
            await ctx.reply(f'{e.__class__.__name__}: {e}')

async def setup(bot):
    await bot.add_cog(Uptime(bot))