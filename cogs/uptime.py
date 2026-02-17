# cogs/uptime.py

import logging
import socket

import discord
import pytz
from discord import Interaction, app_commands
from discord.ext import commands

log = logging.getLogger("discord")


class UptimeCog(commands.Cog):
    """Uptime-related commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.hostname = socket.gethostname()

    @app_commands.command(name="uptime", description="Prints the bot uptime.")
    async def uptime(self, interaction: Interaction):
        try:
            start_time = getattr(self.bot, "startuptime", None)
            if start_time is None:
                await interaction.response.send_message("Startup time is not set.", ephemeral=True)
                return
            uptime = discord.utils.utcnow() - start_time
            d = uptime.days
            h, rem = divmod(uptime.seconds, 3600)
            m, s = divmod(rem, 60)
            msg = f"Uptime: {d}d {h}h {m}m {s}s \N{OK HAND SIGN}"
            await interaction.response.send_message(msg, ephemeral=True)
            log.info("Uptime command ran successfully.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            log.exception("Uptime command failed.")

    @app_commands.command(name="whattimeisit", description="Returns the current time in Eastern Time (Toronto).")
    async def whattimeisit(self, interaction: Interaction):
        try:
            eastern = pytz.timezone("America/Toronto")
            now_utc = discord.utils.utcnow()
            now_eastern = now_utc.astimezone(eastern)
            time_str = now_eastern.strftime("%Y-%m-%d %I:%M %p %Z")
            await interaction.response.send_message(f"I think the time is: {time_str} \N{OK HAND SIGN}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            log.exception("whattimeisit command failed.")


async def setup(bot: commands.Bot):
    await bot.add_cog(UptimeCog(bot))
