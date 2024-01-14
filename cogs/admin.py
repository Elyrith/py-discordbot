#!/usr/bin/env python3
# Discord bot: cogs/admin.py

# Note: Remember to use "cogs.<cogname>" when using load/unload/reload. Example: "/reload cogs.admin"

import logging

import discord
from config import admin_guild, admin_roles
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("discord")


class AdminCog(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.sessions: set[int] = set()

    # Prevent a command from being run by anyone other than a bot admin (currently only the bot owner)
    async def owner_check(self, ctx: commands.Context) -> bool:
        if ctx.user.id != self.bot.owner_id:
            await ctx.response.send_message("Only the bot owner can use this command.", ephemeral=True)
            log.error(f"User {ctx.user} tried to use {ctx.command.name}, but is not the bot owner.")
            return False
        else:
            return True

    async def verify_user_is_admin(self, ctx: commands.Context) -> bool:
        if ctx.guild.id not in admin_roles:
            await ctx.response.send_message("This command is not allowed to be used in this server.", ephemeral=True)
            log.error(f"{ctx.user.name} tried to use {ctx.command.name} in {ctx.guild.name}, but this command is not in the admin_roles in the config file.")
            return False

        admin_role = admin_roles[ctx.guild.id]["admin_role"]
        user_is_admin = False
        for user_role in ctx.user.roles:
            if user_role.name == admin_role:
                user_is_admin = True
                break
        if not user_is_admin:
            await ctx.response.send_message("You do not have permission to run this command.", ephemeral=True)
            log.error(f"{ctx.user.name} tried to use {ctx.command.name} in {ctx.guild.name}, but was not in the role '{admin_role}'. ({ctx.user.roles})")
            return False

        return True

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def load(self, ctx: commands.Context, *, cog: str) -> None:
        """Loads a cog. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.load_extension(cog)
                await ctx.response.send_message(f"Cog {cog} **loaded** successfully. 👌", ephemeral=True)
                log.info(f"Cog {cog} **loaded** successfully. ({ctx.user.name} in {ctx.guild.name})")
            except commands.ExtensionNotFound:
                await ctx.response.send_message(f"Cog {cog} __not found__. 👎", ephemeral=True)
                log.error(f"Tried to load {cog}, but it wasn't found. ({ctx.user.name} in {ctx.guild.name})")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                log.error(f"Tried to load {cog}, but failed. ({ctx.user.name} in {ctx.guild.name})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def unload(self, ctx: commands.Context, *, cog: str) -> None:
        """Unloads a cog. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.unload_extension(cog)
                await ctx.response.send_message(f"Cog {cog} **unloaded** successfully. 👌", ephemeral=True)
                log.info(f"Cog {cog} unloaded successfully. ({ctx.user.name} in {ctx.guild.name})")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                log.error(f"Tried to unload {cog}, but failed. ({ctx.user.name} in {ctx.guild.name})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def reload(self, ctx: commands.Context, *, cog: str) -> None:
        """Reloads a cog, or loads it if it's not loaded. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.load_extension(cog)
                await ctx.response.send_message(f"Cog {cog} __loaded__ successfully. 👌", ephemeral=True)
                log.info(f"Cog {cog} loaded successfully using the reload command. ({ctx.user.name} in {ctx.guild.name})")
                return
            except commands.ExtensionAlreadyLoaded:
                try:
                    await self.bot.reload_extension(cog)
                    await ctx.response.send_message(f"Cog {cog} **reloaded** successfully. 👌", ephemeral=True)
                    log.info(f"Cog {cog} reloaded successfully. ({ctx.user.name} in {ctx.guild.name})")
                except commands.ExtensionError as e:
                    await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                    log.error(f"Tried to reload {cog}, but failed. ({ctx.user.name} in {ctx.guild.name})")
            except commands.ExtensionError as e:
                await ctx.response.send_message(f"{e.__class__.__name__}: {e}", ephemeral=True)
                log.error(f"Tried to reload {cog}, but failed. ({ctx.user.name} in {ctx.guild.name})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def reload_all(self, ctx: commands.Context) -> None:
        """Reloads all currently-loaded cogs. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                loaded_cogs = list(self.bot.extensions.keys())
                for cog in loaded_cogs:
                    try:
                        await self.bot.reload_extension(cog)
                    except Exception as e:
                        await ctx.response.send_message(f"Failed to reload {cog}: {e}", ephemeral=True)
                await ctx.response.send_message("Cogs reloaded successfully. 👌", ephemeral=True)
                await self.bot.tree.sync()
                log.info(f"All cogs unloaded successfully. ({ctx.user.name} in {ctx.guild.name})")
            except Exception as e:
                await ctx.response.send_message(f"Failed to reload all cogs: {e}", ephemeral=True)
                log.error(f"Tried to unload all cogs, but failed. ({ctx.user.name} in {ctx.guild.name})")

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def stop(self, ctx: commands.Context) -> None:
        """Stop the bot. (Bot owner only)"""
        if not await self.owner_check(ctx):
            return
        try:
            await ctx.response.send_message("👍", ephemeral=True)
            await self.bot.close()
            log.info(f"Bot stopped using the stop command. ({ctx.user.name} in {ctx.guild.name})")
        except Exception as e:
            await ctx.response.send_message(f"Unable to stop the bot: {e}", ephemeral=True)
            log.error(f"Tried to stop the bot, but failed. ({ctx.user.name} in {ctx.guild.name})")

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def resync(self, ctx: commands.Context) -> None:
        """Resync all slash commands. Rate-limited. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                await self.bot.tree.sync()
                await ctx.response.send_message("Resync successful. Actual update may take up to an hour. 👌", ephemeral=True)
                log.info(f"Resync successful. ({ctx.user.name} in {ctx.guild.name})")
            except Exception as e:
                await ctx.response.send_message(f"Failed to resync: {e}", ephemeral=True)
                log.error(f"Tried to resync commands, but failed. ({ctx.user.name} in {ctx.guild.name})")
                return

    # Don't use this too much. There is rate-limiting on it and you will have issues.
    @app_commands.command()
    @app_commands.guilds(discord.Object(id=admin_guild))
    async def clear_commands(self, ctx: commands.Context) -> None:
        """Clear all slash commands. Rate-limited. (Admins only)"""
        if await self.verify_user_is_admin(ctx):
            try:
                # Clear and resync all commands
                self.bot.tree.clear_commands()
                await self.bot.tree.sync()
                
                await ctx.response.send_message("Command clear successful. Actual update may take up to an hour. 👌", ephemeral=True)
                log.info(f"Command clear successful. ({ctx.user.name} in {ctx.guild.name})")
            except Exception as e:
                await ctx.response.send_message(f"Failed to clear commands: {e}", ephemeral=True)
                log.error(f"Tried to clear all commands, but failed. ({ctx.user.name} in {ctx.guild.name})")
                return

async def setup(bot) -> None:
    await bot.add_cog(AdminCog(bot))
