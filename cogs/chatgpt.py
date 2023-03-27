#!/usr/bin/env python3
# Loudfoot bot: cogs/chatgpt.py

from discord.ext import commands
import openai

import config

class ChatGPT(commands.Cog):
    def __init__(self, bot, openai_api_token):
        self.bot = bot
        openai.api_key = openai_api_token

    @commands.command()
    async def gpt(self, ctx, *, prompt):
        if not openai.api_key:
            await ctx.reply('The config file does not have a value for openai_api_token.')
            return

        response = openai.Completion.create(
            engine="davinci", prompt=prompt + "\nAnswer the question as accurately as possible without any extra info.", max_tokens=100
        )

        # Get the first text choice from the response
        text = response.choices[0].text.strip()

        # Check if the response is empty or contains an error message
        if not text or text.startswith("Error:"):
            await ctx.reply("I'm sorry, I could not generate a response.")
        else:
            await ctx.reply(text)

async def setup(bot):
    await bot.add_cog(ChatGPT(bot, config.openai_api_token))