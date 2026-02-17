#!/usr/bin/env python3
# Discord bot: cogs/admin.py

# Note: Remember to use "cogs.<cogname>" when using load/unload/reload. Example: "/reload cogs.admin"

import logging

import discord
from discord import app_commands
from discord.ext import commands

from config import admin_guild, admin_roles

log = logging.getLogger("discord")


class AdminCog(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.sessions: set[int] = set()

    # Prevent a command from being run by anyone other than a bot admin (currently only the bot owner)
    async def verify_user_is_owner(self, ctx: discord.Interaction) -> bool:
        if ctx.user.id != self.bot.owner_id:
            await ctx.response.send_message("Only the bot owner can use this command.", ephemeral=True)
            command_name = getattr(getattr(ctx, "command", None), "name", "unknown")
            log.error(f"User {ctx.user} tried to use {command_name}, but is not the bot owner.")
            return False
        else:
            return True

    async def verify_user_is_admin(self, ctx: discord.Interaction) -> bool:
        command_name = getattr(getattr(ctx, "command", None), "name", "unknown")
        user = getattr(ctx, "user", None)
        guild = getattr(ctx, "guild", None)
        user_name = getattr(user, "name", None) or getattr(user, "display_name", "unknown")
        guild_name = getattr(guild, "name", "unknown")

        if not guild or guild.id not in admin_roles:
            await ctx.response.send_message("This command is not allowed to be used in this server.", ephemeral=True)
            log.error(f"{user_name} tried to use {command_name} in {guild_name}, but this guild is not in the admin_roles in the config file.")
            return False

        admin_role = admin_roles[guild.id]["admin_role"]
        user_roles = getattr(user, "roles", [])
        user_is_admin = False
        for user_role in user_roles:
            if getattr(user_role, "name", None) == admin_role:
                user_is_admin = True
                break
        if not user_is_admin:
            await ctx.response.send_message("You do not have permission to run this command.", ephemeral=True)
            log.error(f"{user_name} tried to use {command_name} in {guild_name}, but was not in the role '{admin_role}'. ({user_roles})")
            return False

        return True

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def load(self, ctx: discord.Interaction, *, cog: str) -> None:
        """Loads a cog. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.load_extension(cog)
                await ctx.response.send_message(f"Cog {cog} **loaded** successfully. 👌", ephemeral=True)
                user_name = getattr(getattr(ctx, "user", None), "name", None) or getattr(getattr(ctx, "user", None), "display_name", "unknown")
                guild_name = getattr(getattr(ctx, "guild", None), "name", "unknown")
                log.info(f"Cog {cog} **loaded** successfully. ({user_name} in {guild_name})")
            except commands.ExtensionNotFound:
                await ctx.response.send_message(f"Cog {cog} __not found__. 👎", ephemeral=True)
                log.error(f"Tried to load {cog}, but it wasn't found. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                log.error(f"Tried to load {cog}, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def unload(self, ctx: discord.Interaction, *, cog: str) -> None:
        """Unloads a cog. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.unload_extension(cog)
                await ctx.response.send_message(f"Cog {cog} **unloaded** successfully. 👌", ephemeral=True)
                log.info(f"Cog {cog} unloaded successfully. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                log.error(f"Tried to unload {cog}, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def reload(self, ctx: discord.Interaction, *, cog: str) -> None:
        """Reloads a cog, or loads it if it's not loaded. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.load_extension(cog)
                await ctx.response.send_message(f"Cog {cog} __loaded__ successfully. 👌", ephemeral=True)
                log.info(f"Cog {cog} loaded successfully using the reload command. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
                return
            except commands.ExtensionAlreadyLoaded:
                try:
                    await self.bot.reload_extension(cog)
                    await ctx.response.send_message(f"Cog {cog} **reloaded** successfully. 👌", ephemeral=True)
                    log.info(f"Cog {cog} reloaded successfully. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
                except commands.ExtensionError as e:
                    await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                    log.error(f"Tried to reload {cog}, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                log.error(f"Tried to reload {cog}, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def reload_all(self, ctx: discord.Interaction) -> None:
        """Reloads all currently-loaded cogs. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                loaded_cogs = list(self.bot.extensions.keys())
                for cog in loaded_cogs:
                    try:
                        await self.bot.reload_extension(cog)
                    except Exception as e:
                        await ctx.response.send_message(f"Failed to reload {cog}: {e}", ephemeral=True)
                await ctx.response.send_message("Cogs reloaded successfully. Don't forget to /resync commands if you changed any. 👌", ephemeral=True)
                log.info(f"All cogs unloaded successfully. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
            except Exception as e:
                await ctx.response.send_message(f"Failed to reload all cogs: {e}", ephemeral=True)
                log.error(f"Tried to unload all cogs, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def stop(self, ctx: discord.Interaction) -> None:
        """Stop the bot. (Bot owner only)"""
        if not await self.verify_user_is_owner(ctx):
            return
        try:
            await ctx.response.send_message("👍", ephemeral=True)
            await self.bot.close()
            log.info(f"Bot stopped using the stop command. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
        except Exception as e:
            await ctx.response.send_message(f"Unable to stop the bot: {e}", ephemeral=True)
            log.error(f"Tried to stop the bot, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def resync(self, ctx: discord.Interaction) -> None:
        """Resync all slash commands. Rate-limited. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.tree.sync()
                for guild in self.bot.guilds:
                    await self.bot.tree.sync(guild=guild)
                await ctx.response.send_message("Resync successful. Actual update may take up to an hour. 👌", ephemeral=True)
                log.info(f"Resync successful. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
            except Exception as e:
                await ctx.response.send_message(f"Failed to resync: {e}", ephemeral=True)
                log.error(f"Tried to resync commands, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
                return

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def clear_commands(self, ctx: discord.Interaction) -> None:
        """Clear all slash commands. Rate-limited. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                # Clear and resync all commands
                await ctx.response.send_message("clear_commands has been called. If successful, the bot will not be able to continue running this command after syncing, so there's no way to send a confirmation.", ephemeral=True)
                log.info(f"clear_commands has been called. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')})")
                self.bot.tree.clear_commands(guild=None)
                await self.bot.tree.sync()
                
                # Clear commands from all but the admin guild first. This script stops running when you clear the clear_commands command from the bot, so it has to be last.
                for guild in self.bot.guilds:
                    if guild.id == admin_guild:
                        continue
                    self.bot.tree.clear_commands(guild=guild)
                    await self.bot.tree.sync(guild=guild)
                self.bot.tree.clear_commands(guild=admin_guild)
                await self.bot.tree.sync(guild=admin_guild)
            except Exception as e:
                await ctx.response.send_message(f"Failed to clear commands: {e}", ephemeral=True)
                log.error(f"Tried to clear all commands, but failed. ({getattr(getattr(ctx, 'user', None), 'name', None) or getattr(getattr(ctx, 'user', None), 'display_name', 'unknown')} in {getattr(getattr(ctx, 'guild', None), 'name', 'unknown')}) ({e})")
                return

async def setup(bot) -> None:
    await bot.add_cog(AdminCog(bot))
