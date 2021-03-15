##################
# Import Modules #
##################
from discord.ext import commands
from discord import embeds, Colour, utils
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
        self.lisTeamRoles = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']

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

    ###############
    # Help Button #
    ###############

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        
        ## Difine some of the vairbles from the payload ##
        guild = await self.bot.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        channel = utils.get(await guild.fetch_channels(), id=payload.channel_id)
        
        ## Check reaction is used in the help channel and not the bots reaction ##
        if channel.name != 'help':
            return None

        elif member.id == 787347113188917270:
            return None

        ## Difine the rest of the vairbles from the payload ##
        message =  await channel.fetch_message(payload.message_id) 
        emoji = payload.emoji

        roleMonopolyRunAdministrator = utils.get(member.guild.roles, name='Monopoly Run Administrator')
        ## If reaction is is added to the help message in the help channel ##
        if emoji.name == '👍' and channel.name == 'help' and message.content == 'If you need help click the 👍 button below...':

            ### Gather some info from message ###
            roleMonopolyRunAdministrator = utils.get(member.guild.roles, name='Monopoly Run Administrator')
            strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, member.roles))
            roleTeam = utils.get(member.guild.roles, name=strTeamName) 
            
            ### Check Team and Monopoly Run Administrator Roles exist ###
            if strTeamName == None or roleTeam == None:
                await member.send(':no_entry: You must have a team role! For example role: team1')
                await message.remove_reaction('👍', member)
                return None
      
            elif roleMonopolyRunAdministrator == None:
                await member.send(':no_entry: Could not find the Monopoly Run Administrator Role!')
                await message.remove_reaction('👍', member)
                return None
       
            ### Send message ###
            await message.channel.send(f':confused: {roleMonopolyRunAdministrator.mention}: {roleTeam.mention} Needs Help!')
            await message.remove_reaction('👍', member)

        ## If reaction is added to the the mesage saying x team needs help delete the message ##
        elif emoji.name == '👍' and channel.name == 'help' and message.author.id == 787347113188917270 and roleMonopolyRunAdministrator.name == 'Monopoly Run Administrator':
            await message.delete()


