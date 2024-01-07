#!/usr/bin/env python3
# Discord bot: cogs/admin.py

# Note: Remember to use "cogs.<cogname>" when using load/unload/reload. Example: "!reload cogs.admin"

import logging

import discord
from config import admin_guild
from discord import app_commands
from discord.ext import commands

log = logging.getLogger('discord')


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
            log.info(f"Cog {cog} **loaded** successfully.")
        except commands.ExtensionNotFound:
            await ctx.response.send_message(f"Cog {cog} __not found__. 👎", ephemeral=True)
            log.error(f"Tried to load {cog}, but it wasn't found.")
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)
            log.error(f"Tried to load {cog}, but failed.")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def unload(self, ctx: commands.Context, *, cog: str) -> None:
        """Unloads a cog."""
        try:
            await self.bot.unload_extension(cog)
            await ctx.response.send_message(f"Cog {cog} **unloaded** successfully. 👌", ephemeral=True)
            log.info(f"Cog {cog} unloaded successfully.")
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)
            log.error(f"Tried to unload {cog}, but failed.")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def reload(self, ctx: commands.Context, *, cog: str) -> None:
        """Reloads a cog, or loads it if it's not loaded."""
        try:
            await self.bot.load_extension(cog)
            await ctx.response.send_message(f"Cog {cog} __loaded__ successfully. 👌", ephemeral=True)
            log.info(f"Cog {cog} loaded successfully using the reload command.")
            return
        except commands.ExtensionAlreadyLoaded:
            try:
                await self.bot.reload_extension(cog)
                await ctx.response.send_message(f"Cog {cog} **reloaded** successfully. 👌", ephemeral=True)
                log.info(f"Cog {cog} reloaded successfully.")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)
                log.error(f"Tried to reload {cog}, but failed.")
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}', ephemeral=True)
            log.error(f"Tried to reload {cog}, but failed.")

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
            log.info("All cogs unloaded successfully.")
        except Exception as e:
            await ctx.response.send_message(f"Failed to reload all cogs: {e}", ephemeral=True)
            log.error("Tried to unload all cogs, but failed.")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    @commands.is_owner()
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the bot."""
        try:
            await ctx.response.send_message("👍", ephemeral=True)
            await self.bot.close()
            log.info("Bot stopped using the stop command.")
        except Exception as e:
            await ctx.response.send_message(f"Unable to stop the bot: {e}", ephemeral=True)
            log.error("Tried to stop the bot, but failed.")

    # Don't use the resync commands too much. There is rate-limiting on it and you will have issues.
    async def do_resync(ctx, bot, log):
        try:
            await bot.tree.sync()
            if isinstance(ctx, commands.Context):
                await ctx.send("Resync successful. Actual update may take up to an hour. 👌")
            else:
                await ctx.response.send_message("Resync successful. Actual update may take up to an hour. 👌", ephemeral=True)
            log.info("Resync successful.")
        except Exception as e:
            if isinstance(ctx, commands.Context):
                await ctx.send(f"Failed to resync: {e}")
            else:
                await ctx.response.send_message(f"Failed to resync: {e}", ephemeral=True)
            log.error("Tried to resync commands, but failed.")
            return

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    @commands.is_owner()
    async def resync(self, ctx: commands.Context) -> None:
        """Resync all slash commands. Rate-limited."""
        await self.do_resync(ctx, self.bot, log)

    @commands.command(name='resync')
    @commands.is_owner()
    async def resync_old(self, ctx: commands.Context) -> None:
        """Resync all slash commands. Rate-limited."""
        await self.do_resync(ctx, self.bot, log)

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
            log.info("Command clear successful.")
        except Exception as e:
            await ctx.response.send_message(f"Failed to clear commands: {e}", ephemeral=True)
            log.error("Tried to clear all commands, but failed.")
            return

async def setup(bot) -> None:
    await bot.add_cog(AdminCog(bot))
