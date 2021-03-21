##################
# Import Modules #
###################
from discord.ext import commands
from dotenv import load_dotenv
import os

###########################
# Import External Classes #
###########################
from logging_setup import logging
from game_administration import claAdministration
from game_main import claGame
from game_help import claHelp

##################
# Load .env File #
##################
load_dotenv()

#############
# Setup Bot #
#############
bot = commands.Bot(command_prefix="mr ")

##############
# Setup Cogs #
##############
bot.remove_command('help')  # Remove default help command
bot.add_cog(claHelp(bot))
bot.add_cog(claAdministration(bot))
bot.add_cog(claGame(bot))


@bot.event
async def on_ready():
    logging.info('Reloading / Starting the bot!')


@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('I will send this message when I join a server')
        break


@bot.event
async def on_command_error(ctx, error):
    print(error)


#######
# Run #
#######
logging.info('Bot Started')
bot.run(os.getenv("TOKEN"))
