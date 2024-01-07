#!/usr/bin/env python3
# Discord bot: cogs/events.py

# This requires the following intent: Guild

import logging
import os
from datetime import datetime, timezone

import discord
import yaml
from discord.ext import commands, tasks

log = logging.getLogger('discord')

class EventsCog(commands.Cog):
    """Events stuff."""
    def __init__(self, bot) -> None:
        self.bot = bot
        if not self.post_about_events.is_running():
            self.post_about_events.start()

    # Post about events at various intervals: 24, 1, and 0 hours remaining.
    @tasks.loop(minutes=1)
    async def post_about_events(self) -> None:
        try:
            guilds = self.bot.guilds
            for guild in guilds:
                # Find out if we should even bother getting the list of events. The fetch_scheduled_events function is really slow, so we only want to run it for guilds we don't have a config file for.

                # Get the events channel
                guild_id = guild.id

                # Skip this guild if there's no config file for it.
                filename = f"./cogs/events_config/{guild_id}.yaml"
                if not os.path.isfile(filename):
#                    log.info(f"No file found. {filename} at {os.getcwd()}")
                    continue

                try:
                    with open(filename, "r") as file:
                        data = yaml.safe_load(file)
                        events_channel = data['events_channel']
                        channel = self.bot.get_channel(events_channel)
                except Exception as e:
                    log.error(f"Exception in post_about_events loop when accessing YAML file: {e.__class__.__name__}: {e}")
                    return

                # Fetch the scheduled events for the guild. We do this because guilds.scheduled_events doesn't get updated after the bot has started. The fetch is slow, though.
                guild_events = await guild.fetch_scheduled_events()

                for event in guild_events:

                    # Calculate the number of hours until the event starts.
                    time_until_start = event.start_time - datetime.now(timezone.utc)

                    # Calculate the total number of minutes until the event starts
                    total_minutes_until_start = int(time_until_start.total_seconds() / 60)

                    # Only continue if there's an exact number of minutes until the event starts.
                    # We don't want to notify if there's 59 or 61 minutes remaining, only 60.
                    hours_until_start = total_minutes_until_start // 60
                    minutes_until_start = total_minutes_until_start % 60
                    if not minutes_until_start == 0:
                        continue

                    # Get the event start time.
                    event_start_time = event.start_time.astimezone()
                    event_start_time = event_start_time.strftime('%I:%M %p')

                    # Only if the event is scheduled.
                    if event.status == discord.EventStatus.scheduled or event.status == discord.EventStatus.active:
                        if hours_until_start == 24 or hours_until_start == 1:
                            print(f"[{event.name}]({event.url}) is starting in {hours_until_start} hours. ({event_start_time})")
                            await channel.send(f"[{event.name}]({event.url}) is starting in {hours_until_start} hours. ({event_start_time})")
                        elif hours_until_start == 0:
                            print(f"[{event.name}]({event.url}) is starting now. ({event_start_time})")
                            await channel.send(f"[{event.name}]({event.url}) is starting now. ({event_start_time})")
#                            await event.start()
                            log.info(f"Started event: {event.name} at {event.start_time}")
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
