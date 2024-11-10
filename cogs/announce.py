#!/usr/bin/env python3
# Discord bot: cogs/announce.py

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
for filename in os.listdir("./cogs/announce_config"):
    if filename == ".gitignore" or filename == "000000000000000000.yaml":
        continue # Ignore .gitignore and the template file.
    with open(f"./cogs/announce_config/{filename}", "r") as file:
        guild_id = int(filename.split(".")[0])
        guild_configs[guild_id] = yaml.safe_load(file)


class Announce(commands.Cog):
    """Let users announce they're starting an activity."""
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command()
    async def announce(self, interaction: discord.Interaction, activity: str, hours: int) -> None:
        """Announce you're going to engage in an activity now."""

        try:
            # Skip this guild if there's no config file for it.
            guild_id = interaction.guild_id
            guild_config = guild_configs.get(guild_id)
            if not guild_config:
                await interaction.response.send_message("This server has not been configured to use this command. Let an admin know if you'd like them to configure it.", ephemeral=True)
                log.info(f"Announce: {interaction.user.display_name} used /announce in {interaction.guild.name} but the server has not been configured.")
                return

            # We've got everything now. Send output.
            channel = self.bot.get_channel(guild_config.get("sessions_channel"))

            # Get the role ID for the ping
            notify_role = discord.utils.get(channel.guild.roles, name=guild_config.get("ping"))

            # Send the message(s)
            await channel.send(f"{interaction.user.display_name} is planning to {activity} for {hours} hour(s). <@&{notify_role.id}>")
            await interaction.response.send_message(f"Announced you're {activity} for {hours} hour(s) in channel <{channel.name}>.", ephemeral=True)
            
            log.info(f"Announce: {interaction.user.display_name} used /announce successfully.")
        except Exception as exception:
            await interaction.response.send_message("Command failed, sorry.", ephemeral=True)
            log.error(f"Announce: {interaction.user.display_name} used /announce but it failed. Error was: {exception}")

    @announce.autocomplete(name="activity")
    async def announce_autocomplete_activity(ctx: commands.Context, interaction: discord.Interaction, activity: str) -> List[app_commands.Choice[str]]:
        try:
            # Skip this guild if there's no config file for it.
            guild_id = interaction.guild_id
            guild_config = guild_configs.get(guild_id)
            if not guild_config:
                return []

            activities = guild_config.get("activities")
            return [
            app_commands.Choice(name=activity, value=activity)
            for activity in activities if activity.lower() in activity.lower()
            ]
        except Exception as e:
            log.error(f"Error in announce_autocomplete_activity: {e}")

#    @announce.autocomplete(name="hours")
#    async def announce_autocomplete_hours(ctx: commands.Context, interaction: discord.Interaction, hours: str) -> List[app_commands.Choice[str]]:
#        hours_autocomplete = ["1"]
#        return [
#           app_commands.Choice(name=hours, value=hours)
#           for hours in hours_autocomplete if hours.lower() in hours.lower()
#        ]

    @app_commands.command()
    async def anygame(self, interaction: discord.Interaction, hours: int) -> None:
        """Announce that you're up for gaming for a few hours and welcome an invite."""

        try:
            # Skip this guild if there's no config file for it.
            guild_id = interaction.guild_id
            guild_config = guild_configs.get(guild_id)
            if not guild_config:
                await interaction.response.send_message("This server has not been configured to use this command. Let an admin know if you'd like them to configure it.", ephemeral=True)
                log.info(f"Announce: {interaction.user.display_name} used /anygame in {interaction.guild.name} but the server has not been configured.")
                return

            # We've got everything now. Send output.
            channel = self.bot.get_channel(guild_config.get("sessions_channel"))

            # Get the role ID for the ping
            notify_role = discord.utils.get(channel.guild.roles, name=guild_config.get("ping"))

            # Send the message(s)
            await channel.send(f"{interaction.user.display_name} is available to play something for {hours} hour(s). <@&{notify_role.id}>")
            await interaction.response.send_message(f"Announced you're available to play something for {hours} hour(s) in channel <{channel.name}>.", ephemeral=True)
            
            log.info(f"Announce: {interaction.user.display_name} used /anygame successfully.")
        except Exception as exception:
            await interaction.response.send_message("Command failed, sorry.", ephemeral=True)
            log.error(f"Announce: {interaction.user.display_name} used /anygame but it failed. Error was: {exception}")

async def setup(bot) -> None:
    await bot.add_cog(Announce(bot))
