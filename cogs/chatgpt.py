#!/usr/bin/env python3
# Loudfoot bot: cogs/chatgpt.py

from discord.ext import commands
from discord import app_commands
import openai

from config import openai_api_token

class ChatGPTCog(commands.Cog):
    def __init__(self, bot, openai_api_token) -> None:
        self.bot = bot
        openai.api_key = openai_api_token

    @app_commands.command()
    async def chatgpt(self, ctx: commands.Context, *, prompt) -> None:
        """Access ChatGPT."""
        if not openai.api_key:
            await ctx.response.send_message('The config file does not have a value for openai_api_token.')
            return

        response = openai.Completion.create(
            engine="davinci", prompt=prompt + "\nAnswer the question as accurately as possible without any extra info.", max_tokens=100
        )

        # Get the first text choice from the response
        text = response.choices[0].text.strip()

        # Check if the response is empty or contains an error message
        if not text or text.startswith("Error:"):
            await ctx.response.send_message("I'm sorry, I could not generate a response.")
        else:
            await ctx.response.send_message(text)

async def setup(bot) -> None:
    await bot.add_cog(ChatGPTCog(bot, openai_api_token))