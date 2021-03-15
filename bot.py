##################
# Import Modules #
###################
from discord import utils
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys

##################
# Load .env File #
##################
load_dotenv()

#############
# Setup Bot #
#############
bot = commands.Bot(command_prefix="mr ")

###########################
# Import External Classes #
###########################
from logging_setup import logging
from game_administration import claAdministration
from game_main import claGame
from game_help import claHelp

##############
# Setup Cogs #
##############
bot.remove_command('help') # Remove default help command 
bot.add_cog(claHelp(bot))
bot.add_cog(claAdministration(bot))
bot.add_cog(claGame(bot))

@bot.event
async def on_ready():
    logging.info('Reloading the bot!')

    

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('I will send this message when I join a server')
        break


#######
# Run #
#######
logging.info('Bot Started')
bot.run(os.getenv("TOKEN"))