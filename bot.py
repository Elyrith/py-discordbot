#!/usr/bin/env python3
# Discord bot: bot.py

import logging

import aiohttp
import config
import discord
from discord.ext import commands

description = """Hello! I am DiscordBot."""

log = logging.getLogger("discord")


class DiscordBot(commands.AutoShardedBot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo

    def __init__(self) -> None:
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
        )
        super().__init__(
            command_prefix="!",
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=False,
            activity=discord.Activity(type=discord.ActivityType.listening, name="server fans"),
        )

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id

        for extension in config.initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                log.exception(f"Failed to load extension {extension}. {e}")

        # Add the list of all connected guilds to the log
        for guild in self.guilds:
            log.info(f"Connected to guild: {guild} (ID: {guild.id})")

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self) -> None:
        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()

            # It's not recommended to sync the command tree in on_ready because it can be called multiple times rather than just once when the bot loads. Everyone recommends having a sync command, but how do you implement a command if you don't sync it first? So, the sync commands are in the admin_guild's command tree, so we'll only sync those on_ready, so you can at least resync all using the command if you need to.
            # Maybe the correct solution is to use a regular command rather than an app_command to do syncing.
            await self.tree.sync(guild=discord.Object(id=config.admin_guild))
#            await self.tree.sync()

        log.info("Ready: %s (ID: %s)", self.user, self.user.id)
        for guild in self.guilds:
            log.info(f"Bot is in guild: {guild.name} (ID: {guild.id})")

    async def on_shard_resumed(self, shard_id: int) -> None:
        log.info("Shard ID %s has resumed...", shard_id)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    async def start(self) -> None:
        await super().start(config.discordbot_token, reconnect=True)

    @property
    def config(self) -> None:
        return __import__("config")
