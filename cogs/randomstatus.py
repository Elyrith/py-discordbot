#!/usr/bin/env python3
# Discord bot: cogs/random_status.py

import logging
import os

#from discord import app_commands   # TODO: Add a command to allow people to recommend new status options?
import random

import discord
import yaml
from discord.ext import commands, tasks

log = logging.getLogger("discord")

# Load config file once when bot starts
filename = "./cogs/randomstatus_config/statuses.yaml"
if not os.path.isfile(filename):
    log.error(f"RandomStatus: No config file found. {filename} at {os.getcwd()}")
with open(filename, "r") as file:
    data = yaml.safe_load(file)
    statuses = data["statuses"]


class RandomStatus(commands.Cog):
    """Randomly changes the bot's status every so often."""

    def __init__(self, bot) -> None:
        self.bot = bot
        if not self.update_status.is_running():
            self.update_status.start()

    # Make sure the loop gets stopped if the cog is unloaded.
    def cog_unload(self):
        self.update_status.cancel()

    # Update bot's status every so often.
    @tasks.loop(hours=1)
    async def update_status(self) -> None:
        try:
            # Get a status and set it as the current status
            status = random.choice(statuses)
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))
            log.info(f"RandomStatus: Changed bot status to \"{status}\".")
        except Exception as e:
            log.error(f"RandomStatus: {e.__class__.__name__}: {e}")
            return

    @update_status.before_loop
    async def before_update_status(self) -> None:
        await self.bot.wait_until_ready()

async def setup(bot) -> None:
    await bot.add_cog(RandomStatus(bot))