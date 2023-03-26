#!/usr/bin/env python3
# Discord bot: cogs/test.py

from discord.ext import commands

class Test(commands.Cog):
    """Various test commands."""

    # You can replace the await ctx.reply('Test successful') with your own stuff. (Replace the description in """ too.)
    @commands.command(hidden=True)
    async def test(self, ctx):
        """Test command."""
        await ctx.message.add_reaction("👍")
        try:
            await ctx.reply('Test successful')
            await ctx.message.add_reaction("👌")
        except Exception as e:
            await ctx.reply(f"Command failed.")

async def setup(bot):
    await bot.add_cog(Test(bot))