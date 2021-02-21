##################
# Import Modules #
##################
from discord.ext import commands
from discord import embeds
from database_connection import dbcursor
from logging_setup import logging

##############
# Help Class #
##############
class claHelp(commands.Cog):

    ####################
    # Initialize Class #
    ####################
    def __init__(self, bot):
        self.bot = bot

    ################
    # Help Command #
    ################

    # Command Handling #
    #@bot.group(invoke_without_command=True)
    @commands.command()
    async def help(self, ctx):
        emHelp = embeds.Embed(title = 'Help', description = 'Use &help <command> for detail help', color=0x00ff00)
        emHelp.add_field(name='Test', value="HEllo")

        await ctx.send(embed = emHelp)

    # Error Handling #
    @help.error
    async def help_error(self, ctx, error):
        logging.error(f'Unexpected error: {error}')
        await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')