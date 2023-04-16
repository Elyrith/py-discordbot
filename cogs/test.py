#!/usr/bin/env python3
# Discord bot: cogs/test.py

from discord.ext import commands
from discord import app_commands

class TestCog(commands.Cog):
    """Various test commands."""

    # You can replace the await ctx.response.send_message("Test successful 👌") with your own stuff. (Replace the description in """ too.)
    @app_commands.command(name="test", description="Test command")
    async def test(self, ctx) -> None:
        """Test command."""
        try:
            await ctx.response.send_message("Test successful 👌")
        except Exception as e:
            await ctx.response.send_message(f"Command failed.")

async def setup(bot) -> None:
    await bot.add_cog(TestCog(bot))