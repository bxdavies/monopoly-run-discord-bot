##################
# Import Modules #
##################
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
bot = commands.Bot(command_prefix="&")

###########################
# Import External Classes #
###########################
from logging_setup import logging
from game_setup import claSetup
from game_main import claGame
from game_help import claHelp
from game_auction import claAuction

##############
# Setup Cogs #
##############
bot.remove_command('help') # Remove default help command 
bot.add_cog(claHelp(bot))
bot.add_cog(claSetup(bot))
bot.add_cog(claGame(bot))
bot.add_cog(claAuction(bot))

#######
# Run #
#######
logging.info('Bot Started')
bot.run(os.getenv("TOKEN"))