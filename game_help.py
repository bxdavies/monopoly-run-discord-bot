##################
# Import Modules #
##################
from discord.ext import commands
from discord import embeds, Colour
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
    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        emHelp = embeds.Embed(title = 'Help', description = 'Use &help <command> for detail help', color=Colour.orange())
        emHelp.add_field(name='⠀', value='⠀', inline=False)
        emHelp.add_field(name='Go To', value="&goto")
        emHelp.add_field(name='⠀', value='⠀', inline=False)
        emHelp.add_field(name='Answer', value="&answ")
        emHelp.add_field(name='Own', value="&own")
        emHelp.add_field(name='⠀', value='⠀', inline=False)
        emHelp.add_field(name='I want to sell', value="&iwts")
        emHelp.add_field(name='Bid', value="&bid")
        emHelp.add_field(name='⠀', value='⠀', inline=False)
        emHelp.add_field(name='Money', value="&money")
        emHelp.add_field(name='Owner', value="&owner")
        await ctx.send(embed = emHelp)

    @help.command()
    async def goto(self, ctx):
        emGoToHelp = embeds.Embed(title = 'Go To Command Help', description = 'Use &goto to tell the game which property you are going to visit.', color=Colour.orange())
        emGoToHelp.add_field(name= 'Usage:', value='&goto <property name>')
        emGoToHelp.add_field(name= 'Example Usage:', value='&goto pink2')
        emGoToHelp.add_field(name='⠀', value='⠀', inline=False)
        emGoToHelp.add_field(name='Requirements:', value='1. Property Name must be lowercase. \n2. Property Name should not contain spaces.')
        await ctx.send(embed = emGoToHelp)

    @help.command()
    async def answ(self, ctx):
        emAnswHelp = embeds.Embed(title = 'Answer Command Help', description = 'Use &answ to answer a question at a property.', color=Colour.orange())
        emAnswHelp.add_field(name= 'Usage:', value='&answ <your answer here>')
        emAnswHelp.add_field(name= 'Example Usage:', value='&answ two cats and one Dog')
        emAnswHelp.add_field(name='⠀', value='⠀', inline=False)
        emAnswHelp.add_field(name='Requirements:', value='1. You must have used &answ before using this command.')
        await ctx.send(embed = emAnswHelp)

    @help.command()
    async def own(self, ctx):
        emOwnHelp = embeds.Embed(title = 'Own Command Help', description = 'Use &own to own a property.', color=Colour.orange())
        emOwnHelp.add_field(name= 'Usage:', value='&own <property name>')
        emOwnHelp.add_field(name= 'Example Usage:', value='&own pink2')
        emOwnHelp.add_field(name='⠀', value='⠀', inline=False)
        emOwnHelp.add_field(name='Requirements:', value='1. Property Name must be lowercase. \n2. Property Name should not contain spaces. \n3. You must have answered the question at that property correctly. \n4. This property must not already be owned.')
        await ctx.send(embed = emOwnHelp)

    @help.command()
    async def iwts(self, ctx):
        emIWTSHelp = embeds.Embed(title = 'I Want To Sell Command Help', description = 'Use &iwts to auction off a property.', color=Colour.orange())
        emIWTSHelp.add_field(name= 'Usage:', value='&iwts <property name>')
        emIWTSHelp.add_field(name= 'Example Usage:', value='&iwts pink2')
        emIWTSHelp.add_field(name='⠀', value='⠀', inline=False)
        emIWTSHelp.add_field(name='Requirements:', value='1. Property Name must be lowercase. \n2. Property Name should not contain spaces. \n3. You must own the property.')
        await ctx.send(embed = emIWTSHelp)

    @help.command()
    async def bid(self, ctx):
        emBidHelp = embeds.Embed(title = 'Bid Command Help', description = 'Use &iwts to auction off a property.', color=Colour.orange())
        emBidHelp.add_field(name= 'Usage:', value='&bid <ammount>')
        emBidHelp.add_field(name= 'Example Usage:', value='&bid 200')
        emBidHelp.add_field(name='⠀', value='⠀', inline=False)
        emBidHelp.add_field(name='Requirements:', value='1. You must have answered the question correctly for property your trying to bid on. \n2. You must be able to afford the bid.')
        await ctx.send(embed = emBidHelp)

    @help.command()
    async def money(self, ctx):
        emMoneyHelp = embeds.Embed(title = 'Money Command Help', description = 'Use &money to find out how much money you have.', color=Colour.orange())
        emMoneyHelp.add_field(name= 'Usage:', value='&money')
        emMoneyHelp.add_field(name= 'Example Usage:', value='&money')
        emMoneyHelp.add_field(name='⠀', value='⠀', inline=False)
        emMoneyHelp.add_field(name='Requirements:', value='N/A')
        await ctx.send(embed = emMoneyHelp)


    @help.command()
    async def owner(self, ctx):
        emOwnerHelp = embeds.Embed(title = 'Owner Command Help', description = 'Use &iwts to auction off a property.', color=Colour.orange())
        emOwnerHelp.add_field(name= 'Usage:', value='&owner <property name>')
        emOwnerHelp.add_field(name= 'Example Usage:', value='&owner pink2')
        emOwnerHelp.add_field(name='⠀', value='⠀', inline=False)
        emOwnerHelp.add_field(name='Requirements:', value='N/A')
        await ctx.send(embed = emOwnerHelp)


    # Error Handling #
    @help.error
    async def help_error(self, ctx, error):
        logging.error(f'Unexpected error: {error}')
        await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')
