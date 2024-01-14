#!/usr/bin/env python3
# Discord bot: cogs/gaming_command.py

import logging
import os
from typing import List

import discord
import yaml
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("discord")

# Load YAML files once when bot starts
guild_configs = {}
for filename in os.listdir("./cogs/gaming_announcements_config"):
    if filename == ".gitignore" or filename == "000000000000000000.yaml":
        continue # Ignore .gitignore and the template file.
    with open(f"./cogs/gaming_announcements_config/{filename}", "r") as file:
        guild_id = int(filename.split(".")[0])
        guild_configs[guild_id] = yaml.safe_load(file)


class GamingAnnouncement(commands.Cog):
    """Let users announce they're starting a gaming session."""
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def gaming(self, interaction: discord.Interaction, game: str) -> None:
        """Announce you're going to play a game now."""

        # Get the gaming session channel
        guild = interaction.guild_id
        guild_config = guild_configs.get(guild.id)
        if not guild_config:
            log.error(f"Gaming: No config found for guild {guild.id}")
            return

        sessions_channel = guild_config.get("sessions_channel")
        channel = self.bot.get_channel(sessions_channel)
        notify_role = discord.utils.get(channel.guild.roles, name=guild_config["ping_role"])

        # We've got everything now. Send output.
        try:
            message = await channel.send(f"{interaction.user.display_name} plans to play {game}. <@&{notify_role.id}>")
            log.info(f"Gaming: {interaction.user.display_name} used /gaming successfully.")
        except Exception as exception:
            await interaction.response.send_message("Command failed, sorry.", ephemeral=True)
            log.error(f"Gaming: {interaction.user.display_name} used /gaming but it failed. Message was: {message}. Error was: {exception}")

    @gaming.autocomplete(name="game")
    async def gaming_autocomplete_game(ctx: commands.Context, interaction: discord.Interaction, game: str) -> List[app_commands.Choice[str]]:
        guild = interaction.guild_id
        games = guild_configs[guild.id]["games"]

        return [
           app_commands.Choice(name=game, value=game)
           for game in games if game.lower() in game.lower()
        ]

async def setup(bot) -> None:
    await bot.add_cog(GamingAnnouncement(bot))
