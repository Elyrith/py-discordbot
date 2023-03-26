#!/usr/bin/env python3
# Loudfoot bot: cogs/chatgpt.py

from discord.ext import commands
import config
import openai

class ChatGPTCog(commands.Cog):
    def __init__(self, bot, openai_api_token):
        self.bot = bot
        self.openai_api_token = openai_api_token

    @commands.command()
    async def gpt(self, ctx, *, prompt):
        if not config.openai_api_token:
            await ctx.reply('The config file does not have a value for openai_api_token.')
            return

        response = openai.Completion.create(
            engine="davinci", prompt=prompt, max_tokens=50
        )
        await ctx.reply(response.choices[0].text)

async def setup(bot):
    await bot.add_cog(ChatGPTCog(bot, config.openai_api_token))