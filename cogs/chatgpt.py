#!/usr/bin/env python3
# Loudfoot bot: cogs/chatgpt.py

import logging

import openai
from config import openai_api_token
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("discord")


class ChatGPTCog(commands.Cog):
    def __init__(self, bot, openai_api_token) -> None:
        self.bot = bot
        openai.api_key = openai_api_token

    @app_commands.command()
    async def chatgpt(self, ctx: commands.Context, *, prompt) -> None:
        """Access ChatGPT."""
        if not openai.api_key:
            await ctx.response.send_message("The config file does not have a value for openai_api_token.")
            log.error("ChatGPT: No API key for OpenAI in the config file.")
            return

        response = openai.Completion.create(
            engine="davinci", prompt=prompt + "\nAnswer the question as accurately as possible without any extra info.", max_tokens=100
        )

        # Get the first text choice from the response
        text = response.choices[0].text.strip()

        # Check if the response is empty or contains an error message
        if not text or text.startswith("Error:"):
            await ctx.response.send_message("I'm sorry, I could not generate a response.")
            log.error("ChatGPT: Failed to get a response from OpenAI.")
        else:
            await ctx.response.send_message(text)
            log.info("ChatGPT: Sucessfully got a response from OpenAI.")

async def setup(bot) -> None:
    await bot.add_cog(ChatGPTCog(bot, openai_api_token))
