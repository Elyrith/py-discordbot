#!/usr/bin/env python3
# Discord bot: cogs/announce.py

import logging
import os
from typing import List

import discord
import yaml
from discord import app_commands
from discord.ext import commands
from discord.utils import get

log = logging.getLogger("discord")

# Load YAML files once when bot starts
guild_configs = {}
guild_with_ping_role = []
for filename in os.listdir("./cogs/announce_config"):
    if filename == ".gitignore" or filename == "000000000000000000.yaml":
        continue # Ignore .gitignore and the template file.
    with open(f"./cogs/announce_config/{filename}", "r") as file:
        guild_id = int(filename.split(".")[0])
        guild_configs[guild_id] = yaml.safe_load(file)
        if guild_configs[guild_id].get("ping"): # Only add guilds with a ping role configured to the list of guilds for the command.
            guild_with_ping_role.append(guild_id)


class Announce(commands.Cog):
    """Let users announce they're starting an activity."""
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command()
    @app_commands.guilds(*guild_with_ping_role)
    @app_commands.guild_only()
    async def announce(self, interaction: discord.Interaction, activity: str, hours: int) -> None:
        """Announce you're going to engage in an activity now."""

        try:           
            guild_config = guild_configs.get(interaction.guild_id)
            if not guild_config:
                if not interaction.guild:
                    return
                await interaction.response.send_message("This server has not been configured to use this command. Let an admin know if you'd like them to configure it.", ephemeral=True)
                log.info(f"Announce: {interaction.user.display_name} used /announce in {interaction.guild.name} but the server has not been configured.")
                return # This should never happen because the command is only registered for guilds that have configs with a ping role.

            # We've got everything now. Send output.
            channel = self.bot.get_channel(guild_config.get("sessions_channel"))

            # Get the role ID for the ping
            notify_role = discord.utils.get(channel.guild.roles, name=guild_config.get("ping"))

            # Send the message(s)
            await channel.send(f"{interaction.user.display_name} is planning to play {activity} for {hours} hour(s). <@&{notify_role.id}>")
            await interaction.response.send_message(f"Announced you're playing {activity} for {hours} hour(s) in channel <{channel.name}>.", ephemeral=True)
            
            log.info(f"Announce: {interaction.user.display_name} used /announce successfully.")
        except Exception as exception:
            await interaction.response.send_message("Command failed, sorry.", ephemeral=True)
            log.error(f"Announce: {interaction.user.display_name} used /announce but it failed. Error was: {exception}")

    @announce.autocomplete(name="activity")
    async def announce_autocomplete_activity(self, interaction: discord.Interaction, activity: str) -> List[app_commands.Choice[str]]:
        try:
            # Skip this guild if there's no config file for it.
            guild_config = guild_configs.get(interaction.guild_id)
            if not guild_config:
                return []

            activities = guild_config.get("activities") or []
            return [
                app_commands.Choice(name=act, value=act)
                for act in activities if activity.lower() in act.lower()
            ]
        except Exception as e:
            log.error(f"Error in announce_autocomplete_activity: {e}")
            return []

#    @announce.autocomplete(name="hours")
#    async def announce_autocomplete_hours(ctx: commands.Context, interaction: discord.Interaction, hours: str) -> List[app_commands.Choice[str]]:
#        hours_autocomplete = ["1"]
#        return [
#           app_commands.Choice(name=hours, value=hours)
#           for hours in hours_autocomplete if hours.lower() in hours.lower()
#        ]

    @app_commands.command()
    @app_commands.guilds(*guild_with_ping_role)
    @app_commands.guild_only()
    async def anygame(self, interaction: discord.Interaction, hours: int) -> None:
        """Announce that you're up for gaming for a few hours and welcome an invite."""

        try:
            # Skip this guild if there's no config file for it.
            guild_id = interaction.guild_id
            guild_config = guild_configs.get(guild_id)
            if not guild_config:
                await interaction.response.send_message("This server has not been configured to use this command. Let an admin know if you'd like them to configure it.", ephemeral=True)
                if not interaction.guild:
                    return
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

    @app_commands.command()
    @app_commands.guilds(*guild_with_ping_role) # Remove this line to make it a global command.
    @app_commands.guild_only()
    async def ping_role_add_me(self, interaction: discord.Interaction) -> None:
        """Add the user to the ping role, as defined by guild_configs[guild_id].ping in the config file for the server."""

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        ping_role_name = guild_configs[guild_id].get("ping")

        ping_role = get(guild.roles, name=ping_role_name)
        if not ping_role:
            await interaction.response.send_message(f"The configured ping role ({ping_role_name} does not exist on this server.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_add_me in guild {guild_id} but the ping role does not exist.")
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message(f"{interaction.user} not found in server {guild_id}.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_add_me in guild {guild_id} but was not found as a member.")
            return

        if any(r.name == ping_role_name for r in member.roles):
            await interaction.response.send_message(f"You already have role {ping_role_name} on server {guild_id}.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_add_me in guild {guild_id} but is already in the ping role.")
            return

        try:
            await member.add_roles(ping_role, reason=f"{self.bot.user} adding user to {ping_role_name} role.")
            await interaction.response.send_message(f"You have been added to the {ping_role.name} role!", ephemeral=True)
            log.info(f"User {interaction.user} used ping_role_add_me in guild {guild_id} and was added to the ping role.")
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to add you to the ping role. Please contact an administrator on {guild_id}.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_add_me in guild {guild_id} but the bot does not have permission to add roles on this server.")


    @app_commands.command()
    @app_commands.guilds(*guild_with_ping_role) # Remove this line to make it a global command.
    @app_commands.guild_only()
    async def ping_role_remove_me(self, interaction: discord.Interaction) -> None:
        """Remove the user from the ping role, as defined by guild_configs[guild_id].ping in the config file for the server."""

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        ping_role_name = guild_configs[guild_id].get("ping")

        ping_role = get(guild.roles, name=ping_role_name)
        if not ping_role:
            await interaction.response.send_message(f"The configured ping role ({ping_role_name} does not exist on this server.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_remove_me in guild {guild_id} but the ping role does not exist.")
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message(f"{interaction.user} not found in server {guild_id}.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_remove_me in guild {guild_id} but was not found as a member.")
            return

        if not any(r.name == ping_role_name for r in member.roles):
            await interaction.response.send_message(f"You do not have role {ping_role_name} on server {guild_id}.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_remove_me in guild {guild_id} but is not in the ping role.")
            return

        try:
            await member.remove_roles(ping_role, reason=f"{self.bot.user} adding user to {ping_role_name} role.")
            await interaction.response.send_message(f"You have been removed from the {ping_role.name} role!", ephemeral=True)
            log.info(f"User {interaction.user} used ping_role_remove_me in guild {guild_id} and was removed from the ping role.")
        except discord.Forbidden:
            await interaction.response.send_message("I do not have permission to add you to the ping role. Please contact an administrator on {guild_id}.", ephemeral=True)
            log.info(f"User {interaction.user} attempted to use ping_role_remove_me in guild {guild_id} but the bot does not have permission to add roles on this server.")


async def setup(bot) -> None:
    await bot.add_cog(Announce(bot))
