#!/usr/bin/env python3
# Discord bot: cogs/admin.py

# Note: Remember to use "cogs.<cogname>" when using load/unload/reload. Example: "!reload cogs.admin"

import logging

import discord
from discord.ext import commands
from discord import app_commands

from config import admin_guild

log = logging.getLogger('discord.cogs')

class AdminCog(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.sessions: set[int] = set()

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def load(self, ctx: commands.Context, *, cog: str) -> None:
        """Loads a cog."""
        try:
            await self.bot.load_extension(cog)
            await ctx.response.send_message(f"Cog {cog} **loaded** successfully. 👌", ephemeral=True)
        except commands.ExtensionNotFound as e:
            await ctx.response.send_message(f"Cog {cog} __not found__. 👎", ephemeral=True)
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def unload(self, ctx: commands.Context, *, cog: str) -> None:
        """Unloads a cog."""
        try:
            await self.bot.unload_extension(cog)
            await ctx.response.send_message(f"Cog {cog} **unloaded** successfully. 👌", ephemeral=True)
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def reload(self, ctx: commands.Context, *, cog: str) -> None:
        """Reloads a cog, or loads it if it's not loaded."""
        try:
            await self.bot.load_extension(cog)
            await ctx.response.send_message(f"Cog {cog} __loaded__ successfully. 👌", ephemeral=True)
            return
        except commands.ExtensionAlreadyLoaded as e:
            try:
                await self.bot.reload_extension(cog)
                await ctx.response.send_message(f"Cog {cog} **reloaded** successfully. 👌", ephemeral=True)
            except commands.ExtensionError as e:
                await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)

    async def reload_or_load_extension(self, cog: str) -> None:
        try:
            await self.bot.reload_extension(cog)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(cog)

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    @commands.is_owner()
    async def reload_all(self, ctx: commands.Context) -> None:
        """Reloads all currently-loaded cogs"""
        try:
            loaded_cogs = list(self.bot.extensions.keys())
            for cog in loaded_cogs:
                try:
                    await self.bot.reload_extension(cog)
                except Exception as e:
                    await ctx.response.send_message(f"Failed to reload {cog}: {e}", ephemeral=True)
            await ctx.response.send_message("Cogs reloaded successfully. 👌", ephemeral=True)
            await self.bot.tree.sync()
        except Exception as e:
            await ctx.response.send_message(f"Failed to reload all cogs: {e}", ephemeral=True)

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    @commands.is_owner()
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the bot."""
        try:
            await ctx.response.send_message("👍", ephemeral=True)
            await self.bot.close()
        except:
            await ctx.response.send_message(f"Unable to stop the bot for some reason.", ephemeral=True)

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    @commands.is_owner()
    async def resync(self, ctx: commands.Context) -> None:
        """Resync all slash commands. Rate-limited."""
        try:
            await self.bot.tree.sync()
            await ctx.response.send_message("Resync successful. Actual update may take up to an hour. 👌", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Failed to resync: {e}", ephemeral=True)
            return

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    @commands.is_owner()
    async def clear_commands(self, ctx: commands.Context) -> None:
        """Clear all slash commands. Rate-limited."""
        try:
            # Clear and resync all commands
            self.bot.tree.clear_commands()
            await self.bot.tree.sync()
            
            await ctx.response.send_message("Command clear successful. Actual update may take up to an hour. 👌", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"Failed to clear commands: {e}", ephemeral=True)
            return

async def setup(bot) -> None:
    await bot.add_cog(AdminCog(bot))