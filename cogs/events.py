#!/usr/bin/env python3
# Discord bot: cogs/events.py

# This module posts in a Discord channel when there's an event in the server.
# The config files should be in cogs/events_config and named <guild_id>.yaml. It will skip any guild without a config file.

# This requires the following intent: Guild

import asyncio
import logging
import os
from datetime import datetime, timezone

import discord
import yaml
from discord.ext import commands, tasks

log = logging.getLogger("discord")

# Load YAML files once when bot starts
guild_configs = {}
for filename in os.listdir("./cogs/events_config"):
    if filename == ".gitignore" or filename == "000000000000000000.yaml":
        continue # Ignore .gitignore and the template file.
    with open(f"./cogs/events_config/{filename}", "r") as file:
        guild_id = int(filename.split(".")[0])
        guild_configs[guild_id] = yaml.safe_load(file)


class EventsCog(commands.Cog):
    """Events stuff."""
    def __init__(self, bot) -> None:
        self.bot = bot
        if not self.post_about_events.is_running():
            self.post_about_events.start()

    async def event_posting(self, guild, channel, current_time):
        # Fetch the scheduled events for the guild. We do this because guilds.scheduled_events doesn't get updated after the bot has started. The fetch is slow, though.
        guild_events = await guild.fetch_scheduled_events()

        for event in guild_events:

            # Calculate the number of hours until the event starts.
            time_until_start = event.start_time - current_time

            # Calculate the total number of minutes until the event starts, rounding up.
            total_minutes_until_start = int(time_until_start.total_seconds() // 60 + 1)

            # Only continue if there's an exact number of minutes until the event starts.
            # We don't want to notify if there's 59 or 61 minutes remaining, only 60.
            hours_until_start = total_minutes_until_start // 60
            minutes_until_start = total_minutes_until_start % 60
            if not minutes_until_start == 0:
                continue

            # Get the event start time.
            event_start_time = event.start_time.astimezone()
            event_start_time = event_start_time.strftime("X%I:%M %p").replace("X0","X").replace("X","")

            notify_role = discord.utils.get(channel.guild.roles, name=guild_configs[guild.id]["ping_role"])

            # Only if the event is scheduled.
            if event.status == discord.EventStatus.scheduled or event.status == discord.EventStatus.active:
                if 0 in guild_configs[guild.id]["announce_times"] and hours_until_start == 0:
                    log.info(f"Message posted: [{event.name}]({event.url}) is starting now. <@&{notify_role.id}>")
                    await channel.send(f"[{event.name}]({event.url}) is starting now. <@&{notify_role.id}>")
                elif hours_until_start in guild_configs[guild.id]["announce_times"]:
                    log.info(f"Message posted: [{event.name}]({event.url}) is starting in {hours_until_start} hour(s). <@&{notify_role.id}>")
                    await channel.send(f"[{event.name}]({event.url}) is starting in {hours_until_start} hour(s). <@&{notify_role.id}>")




    # Post about events at various intervals. Use ./events_config/ files to configure your settings.
    @tasks.loop(minutes=1)
    async def post_about_events(self) -> None:
        # Events can't be scheduled except at 00, 15, 30, and 45 minutes past the hour, so only run then.
        current_time = datetime.now(timezone.utc)
        if current_time.minute not in [00, 15, 30, 45]:
            return

        try:
            for guild in self.bot.guilds:
                # Find out if we should even bother getting the list of events. The fetch_scheduled_events function is really slow, so we only want to run it for guilds we don't have a config file for.

                # Skip this guild if there's no config file for it.
                guild_config = guild_configs.get(guild.id)
                if not guild_config:
                    continue

                events_channel = guild_config.get("events_channel")
                channel = self.bot.get_channel(events_channel)

                # Do the actual posting ascynchronously because the fetch_scheduled_events function is so slow.
                asyncio.create_task(self.event_posting(guild, channel, current_time))

        except Exception as e:
            await log.error(f"Exception in post_about_events loop: {e}.")

    # Make sure the loop gets stopped if the cog is unloaded.
    def cog_unload(self):
        self.post_about_events.cancel()

    @post_about_events.before_loop
    async def before_post_about_events(self) -> None:
        await self.bot.wait_until_ready()

async def setup(bot) -> None:
    await bot.add_cog(EventsCog(bot))
