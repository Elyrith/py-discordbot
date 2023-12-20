#!/usr/bin/env python3
# Discord bot: cogs/gaming.py

import asyncio
import logging
import os
from typing import List

import discord
import yaml
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("discord")

class GamingAnnouncement(commands.Cog):
    """Let users announce they're starting a gaming session."""
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def gaming(self, interaction: discord.Interaction, game: str, hours: int) -> None:
        """Announce you're going to play a game now."""

        # Get the gaming session channel
        guild = interaction.guild_id
        filename = f"./cogs/gaming_config/{guild}.yaml"
        if not os.path.isfile(filename):
            log.error(f"Gaming: No file found. {filename} at {os.getcwd()}")
            return

        try:
            with open(filename, "r") as file:
                data = yaml.safe_load(file)
                sessions_channel = data["sessions_channel"]
                ping = data["ping"]
        except Exception as exception:
            log.error(f"Gaming: {exception.__class__.__name__}: {exception}")
            return

        # We've got everything now. Send output.
        channel = self.bot.get_channel(sessions_channel)
        try:
            # Get the role ID for the ping
            notify_role = discord.utils.get(channel.guild.roles, name=ping)

            # Send the message(s)
            message = await channel.send(f"{interaction.user.display_name} plans to play {game} for {hours} hour(s). <@&{notify_role.id}>")
            log.info(f"Gaming: {interaction.user.display_name} used /gaming successfully.")
        except Exception as exception:
            await interaction.response.send_message("Command failed, sorry.", ephemeral=True)
            log.error(f"Gaming: {interaction.user.display_name} used /gaming but it failed. Message was: {message}. Error was: {exception}")

        # Delete the message after the {hours} have passed, default to 1 hour if the value isn't an integer.
        if not isinstance(hours, int):
            hours = 1

        try:
            await asyncio.sleep(hours * 60 * 60)
            await message.delete()
            log.info(f"Gaming: Successfully auto-deleted a message I sent: {message}")
        except Exception as e:
            log.error(f"Gaming: Could not auto-delete a message I sent. {e.__class__.__name__}: {e}")

    @gaming.autocomplete(name="game")
    async def gaming_autocomplete_game(ctx: commands.Context, interaction: discord.Interaction, game: str) -> List[app_commands.Choice[str]]:
        # Get the gaming session channel
        guild = interaction.guild_id
        filename = f"./cogs/gaming_config/{guild}.yaml"
        if not os.path.isfile(filename):
            log.error(f"Gaming: No file found. {filename} at {os.getcwd()}")
            return []

        try:
            with open(filename, "r") as file:
                data = yaml.safe_load(file)
                games = data["games"]
        except Exception as exception:
            log.error(f"Gaming: {exception.__class__.__name__}: {exception}")
            return []

        return [
           app_commands.Choice(name=game, value=game)
           for game in games if game.lower() in game.lower()
        ]

async def setup(bot) -> None:
    await bot.add_cog(GamingAnnouncement(bot))