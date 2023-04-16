#!/usr/bin/env python3
# Discord bot: cogs/admin.py

# Note: Remember to use "cogs.<cogname>" when using load/unload/reload. Example: "!reload cogs.admin"

import discord
from discord.ext import commands
from discord import app_commands

import config

class AdminCog(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.sessions: set[int] = set()

    @app_commands.command(name="load", description="Loads a module")
    async def load(self, ctx, *, module: str) -> None:
        """Loads a module."""
        try:
            await self.bot.load_extension(module)
            await ctx.response.send_message("Module {module} loaded successfully. 👌")
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}')

    @app_commands.command(name="unload", description="Unloads a module")
    async def unload(self, ctx, *, module: str) -> None:
        """Unloads a module."""
        try:
            await self.bot.unload_extension(module)
            await ctx.response.send_message("Module {module} unloaded successfully. 👌")
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}')

    @app_commands.command(name="reload", description="Reloads a module, or loads it if it's not loaded")
    async def reload(self, ctx, *, module: str) -> None:
        """Reloads a module, or loads it if it's not loaded."""
        try:
            await self.bot.reload_extension(module)
            await ctx.response.send_message("Module {module} reloaded successfully. 👌")
            return
        except commands.ExtensionError as e:
            try:
                await self.bot.load_extension(module)
                await ctx.response.send_message("Module {module} reloaded successfully. 👌")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f'{e.__class__.__name__}: {e}')

    async def reload_or_load_extension(self, module: str) -> None:
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(module)

    @app_commands.command(name="reload_all", description="Reloads all currently-loaded cogs")
    @commands.is_owner()
    async def reload_all(self, ctx) -> None:
        """Reloads all currently-loaded cogs"""
        loaded_cogs = list(self.bot.extensions.keys())
        for cog in loaded_cogs:
            try:
                await self.bot.reload_extension(cog)
                return
            except Exception as e:
                await ctx.response.send_message(f"Failed to reload {cog}: {e}")
        await ctx.response.send_message("Modules reloaded successfully. 👌")

    @app_commands.command(name="stop", description="Stop the bot")
    @commands.is_owner()
    async def stop(self, ctx) -> None:
        """Stop the bot."""
        try:
            await ctx.response.send_message("👍")
            await self.bot.close()
        except:
            await ctx.response.send_message(f"Unable to stop the bot for some reason.")

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command(name="resync", description="Resync all app_commands")
    async def resync(self, ctx) -> None:
        """Resync all app_commands."""
        try:
            self.bot.tree.clear_commands(guild=discord.Object(id=config.admin_guild))
            self.bot.tree.copy_global_to(guild=discord.Object(id=config.admin_guild))
            await self.bot.tree.sync(guild=discord.Object(id=config.admin_guild))
        except Exception as e:
            await ctx.response.send_message(f"Failed to resync: {e}")
            return
        await ctx.response.send_message("Resync successful. Actual update may take time. 👌")

async def setup(bot) -> None:
    await bot.add_cog(AdminCog(bot))