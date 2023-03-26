#!/usr/bin/env python3
# Discord bot: cogs/admin.py

# Note: Remember to use "cogs.<cogname>" when using load/unload/reload. Example: "!reload cogs.admin"

from discord.ext import commands

class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot
        self.sessions: set[int] = set()

    @commands.command(hidden=True)
    async def load(self, ctx, *, module: str):
        """Loads a module."""
        try:
            await ctx.message.add_reaction("👍")
            await self.bot.load_extension(module)
            await ctx.message.add_reaction("👌")
        except commands.ExtensionError as e:
            await ctx.reply(f'{e.__class__.__name__}: {e}')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module: str):
        """Unloads a module."""
        try:
            await ctx.message.add_reaction("👍")
            await self.bot.unload_extension(module)
            await ctx.message.add_reaction("👌")
        except commands.ExtensionError as e:
            await ctx.reply(f'{e.__class__.__name__}: {e}')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module: str):
        """Reloads a module, or loads it if it's not loaded."""
        try:
            await ctx.message.add_reaction("👍")
            await self.bot.reload_extension(module)
            await ctx.message.add_reaction("👌")
        except commands.ExtensionError as e:
            try:
                await self.bot.load_extension(module)
                await ctx.message.add_reaction("👌")
            except commands.ExtensionError as e:
                await ctx.reply(f'{e.__class__.__name__}: {e}')

    async def reload_or_load_extension(self, module: str) -> None:
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(module)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload_all(self, ctx):
        """Reloads all currently-loaded cogs"""
        try:
            await ctx.message.add_reaction("👍")
        except Exception as e:
            await ctx.reply(f"Failed to react with a thumbsup emoji.")
        
        loaded_cogs = list(self.bot.extensions.keys())
        for cog in loaded_cogs:
            try:
                self.bot.reload_extension(cog)
                await ctx.message.add_reaction("👌")
            except Exception as e:
                await ctx.reply(f"Failed to reload {cog}: {e}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def stop(self, ctx):
        """Stop the bot."""
        try:
            await ctx.message.add_reaction("👍")
            await self.bot.close()
        except:
            await ctx.reply(f"Unable to stop the bot for some reason.")

async def setup(bot):
    await bot.add_cog(Admin(bot))