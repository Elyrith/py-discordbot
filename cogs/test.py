#!/usr/bin/env python3
# Discord bot: cogs/test.py

import discord
from discord.ext import commands
from discord import app_commands
import logging

from config import admin_guild

log = logging.getLogger(__name__)

class TestCog(commands.Cog):
    """Various test commands."""

    # You can replace the await ctx.response.send_message("Test successful 👌") with your own stuff. (Replace the description in """ too.)
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild)) # Remove this line to make it a global command.
    async def test(self, ctx: commands.Context) -> None:
        """Test command."""
        try:
            await ctx.response.send_message("Test successful 👌")
            log.info(f"Command {ctx.command} was executed successfully in {ctx.guild.name}.")
        except Exception as e:
            await ctx.response.send_message(f"Command failed.", ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(TestCog(bot))