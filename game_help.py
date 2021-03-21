##################
# Import Modules #
##################
from discord.ext import commands
from discord import embeds, Colour, utils
import re

###########################
# Import External Classes #
###########################
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
        self.funTeamRole = claHelp.funTeamRole

    #############
    # Functions #
    #############

    # Return users team role #
    async def funTeamRole(member, message):
        lismyRoles = [r.name for r in member.roles]
        lismyRoles.reverse()
        r = re.compile("team.*")
        if not list(filter(r.match, lismyRoles)):
            await message.remove_reaction('👍', member)
            raise commands.MissingRole("team?")

        return utils.get(member.roles, name=next(filter(r.match, lismyRoles)))

    ################
    # Help Command #
    ################

    # Command Handling #
    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        emHelp = embeds.Embed(
            title='Help',
            description='Use mr help <command> for detail help',
            color=Colour.orange()
        )
        emHelp.add_field(name='⠀', value='⠀', inline=False)
        emHelp.add_field(name='Go To', value="mr goto")
        emHelp.add_field(name='Answer', value="mr answ")
        emHelp.add_field(name='⠀', value='⠀', inline=False)
        emHelp.add_field(name='Money', value="mr money")
        emHelp.add_field(name='Owner', value="mr owner")
        await ctx.send(embed=emHelp)

    @help.command()
    async def goto(self, ctx):
        emGoToHelp = embeds.Embed(
            title='Go To Command Help',
            description='Use mr goto to tell the game which property you are going to visit.',
            color=Colour.orange()
        )
        emGoToHelp.add_field(name='Usage:', value='mr goto <property name>')
        emGoToHelp.add_field(name='Example Usage:', value='mr goto pink2')
        emGoToHelp.add_field(name='⠀', value='⠀', inline=False)
        emGoToHelp.add_field(name='Requirements:', value='1. Property Name must be lowercase. \n2. Property Name should not contain spaces.')
        await ctx.send(embed=emGoToHelp)

    @help.command()
    async def answ(self, ctx):
        emAnswHelp = embeds.Embed(
            title='Answer Command Help',
            description='Use mr answ to answer a question at a property.',
            color=Colour.orange()
        )
        emAnswHelp.add_field(name='Usage:', value='mr answ <your answer here>')
        emAnswHelp.add_field(name='Example Usage:', value='mr answ two cats and one Dog')
        emAnswHelp.add_field(name='⠀', value='⠀', inline=False)
        emAnswHelp.add_field(name='Requirements:', value='1. You must have used mr goto before using this command.')
        await ctx.send(embed=emAnswHelp)

    @help.command()
    async def money(self, ctx):
        emMoneyHelp = embeds.Embed(
            title='Money Command Help',
            description='Use mr money to find out how much money you have.',
            color=Colour.orange()
        )
        emMoneyHelp.add_field(name='Usage:', value='mr money')
        emMoneyHelp.add_field(name='Example Usage:', value='mr money')
        emMoneyHelp.add_field(name='⠀', value='⠀', inline=False)
        emMoneyHelp.add_field(name='Requirements:', value='N/A')
        await ctx.send(embed=emMoneyHelp)

    @help.command()
    async def owner(self, ctx):
        emOwnerHelp = embeds.Embed(
            title='Owner Command Help',
            description='Use mr owner to find the owner of a property.',
            color=Colour.orange()
        )
        emOwnerHelp.add_field(name='Usage:', value='mr owner <property name>')
        emOwnerHelp.add_field(name='Example Usage:', value='mr owner pink2')
        emOwnerHelp.add_field(name='⠀', value='⠀', inline=False)
        emOwnerHelp.add_field(name='Requirements:', value='N/A')
        await ctx.send(embed=emOwnerHelp)

    ###############
    # Help Button #
    ###############
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        # Define some of the variables from the payload #
        guild = await self.bot.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        channel = utils.get(await guild.fetch_channels(), id=payload.channel_id)

        # Check reaction is used in the help channel and not the bots reaction #
        if channel.name != 'help':
            return None

        elif member.id == 787347113188917270:
            return None

        # Define the rest of the variables from the payload #
        message = await channel.fetch_message(payload.message_id)
        emoji = payload.emoji

        roleMonopolyRunAdministrator = utils.get(member.guild.roles, name='Monopoly Run Administrator')
        # If reaction is is added to the help message in the help channel #
        if emoji.name == '👍' and channel.name == 'help' and message.content == 'If you need help click the 👍 button below...':

            # Gather some info from message #
            roleMonopolyRunAdministrator = utils.get(member.guild.roles, name='Monopoly Run Administrator')
            roleTeam = await self.funTeamRole(member, message)

            # Check Team and Monopoly Run Administrator Roles exist #
            if roleMonopolyRunAdministrator is None:
                await member.send(':no_entry: Could not find the Monopoly Run Administrator Role!')
                await message.remove_reaction('👍', member)
                return None

            # Send message #
            await message.channel.send(f':confused: {roleMonopolyRunAdministrator.mention}: {roleTeam.mention} Needs Help!')
            await message.remove_reaction('👍', member)

        # If reaction is added to the the message saying x team needs help delete the message #
        elif emoji.name == '👍' and channel.name == 'help' and message.author.id == 787347113188917270 and roleMonopolyRunAdministrator.name == 'Monopoly Run Administrator':
            await message.delete()

    ##################
    # Error Handling #
    ##################
    async def cog_command_error(self, ctx, error):

        # Missing Role #
        if isinstance(error, commands.MissingRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')

        # No Private Message #
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(':no_entry: Please use all commands in a Server (Not Direct Messages)!')

        # Any other error #
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: (Main)An unexpected error occurred! ```The error is: {error}``` ')
