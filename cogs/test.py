#!/usr/bin/env python3
# Discord bot: cogs/test.py

import logging

import discord
from config import admin_guild
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("discord")


class TestCog(commands.Cog):
    """Various test commands."""

    # You can replace the await ctx.response.send_message("Test successful 👌") with your own stuff. (Replace the description in """ too.)
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild)) # Remove this line to make it a global command.
    async def test(self, ctx: commands.Context) -> None:
        """Test command."""
        try:
            await ctx.response.send_message("Test successful 👌")
            log.info(f"Test: Command {ctx.command.name} was executed successfully in {ctx.guild.name}.")
        except Exception:
            await ctx.response.send_message("Command failed.", ephemeral=True)
            log.error(f"Test: Command {ctx.command.name} was failed in {ctx.guild.name}.")

async def setup(bot) -> None:
    await bot.add_cog(TestCog(bot))
