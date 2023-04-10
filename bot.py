#!/usr/bin/env python3
# Discord bot: bot.py

import logging

import discord
from discord.ext import commands
import aiohttp

import config

description = """
Hello! I am DiscordBot.
"""

log = logging.getLogger(__name__)

initial_extensions = (
    'cogs.admin',
    'cogs.uptime',
    'cogs.thecatapi'
)

class DiscordBot(commands.AutoShardedBot):
    user: discord.ClientUser
    bot_app_info: discord.AppInfo

    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
            members=False,
            messages=True,
            message_content=True,
        )
        super().__init__(
            command_prefix='!',
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
        )

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                log.exception('Failed to load extension %s.', extension)

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="server fans"))

        log.info('Ready: %s (ID: %s)', self.user, self.user.id)

    async def on_shard_resumed(self, shard_id: int):
        log.info('Shard ID %s has resumed...', shard_id)

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
    def config(self):
        return __import__('config')