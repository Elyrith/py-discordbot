#!/usr/bin/env python3
# Loudfoot bot: cogs/thecatapi.py

from discord.ext import commands
from discord import app_commands
import requests

import config

class TheCatAPICog(commands.Cog):
    """TheCatAPI stuff."""

    def __init__(self, bot, thecatapi_token):
        self.bot = bot
        self.thecatapi_token = thecatapi_token

    @app_commands.command(name="gimmeacat", description="Gets and shows a cat photo")
    async def gimmeacat(self, ctx) -> None:
        """Gets and shows a cat photo."""

        # Check if the token is found
#        if not config.thecatapi_token:
#            await ctx.reply('The config file does not have a value for thecatapi_token.')
#            return

        try:
            catrequest = requests.get('https://api.thecatapi.com/v1/images/search','Content-Type: application/json')
            #, headers = {"x-api-key": config.thecatapi_token})
            catjson = catrequest.json()
            caturl = catjson[0]["url"]

            await ctx.response.send_message("Prepare for this cuteness: " + caturl)
        except commands.ExtensionError as e:
            await ctx.response.send_message(f'{e.__class__.__name__}: {e}')


async def setup(bot):
    await bot.add_cog(TheCatAPICog(bot, config.thecatapi_token))