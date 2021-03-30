#########
# Import Modules #
#########
from discord.ext import commands, tasks
from discord import utils, embeds, Colour
import re

##############
# Import External Classes #
##############
from database_connection import dbcursor
from logging_setup import logging
import errors as MonopolyRunError


###############
# Setup Class #
###############
class claAdministration(commands.Cog):

    ####################
    # Initialize Class #
    ####################
    def __init__(self, bot):
        self.bot = bot
        self.UpdatePropertiesChannel = claAdministration.UpdatePropertiesChannel
        self.UpdateLeaderBoard = claAdministration.UpdateLeaderBoard

    #################
    # Setup Command #
    #################

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx, intNumberOfTeams: int, strQuestionSet):

        # Declare some variables for later #
        strGuildID = str(ctx.guild.id)
        strGuildName = str(ctx.guild.name)
        intGuildID = int(ctx.guild.id)
        lisRoles = []

        # Check if guild is already setup #
        dbcursor.execute("SELECT id FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisExists = dbcursor.fetchall()
        for item in lisExists:
            if intGuildID == item[0]:
                await ctx.send(':no_entry: You have already run setup!')
                return None

        # Check Question set exists #
        dbcursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE ?", (f'tbl_{strQuestionSet}', ))
        lisQuestionSet = dbcursor.fetchall()
        if not lisQuestionSet:
            await ctx.send(':no_entry: That question set was not found!')
            return None

        # Check number of teams is greater than 2 and less than 46 #
        if intNumberOfTeams < 2:
            raise MonopolyRunError.NotEnoughTeams()
        elif intNumberOfTeams >= 47:
            raise MonopolyRunError.TooManyTeams()

        # Declare lisTeams based on user input #
        lisTeams = []
        for i in range(intNumberOfTeams):
            lisTeams.append(f'team{i+1}')

        # Create Monopoly Run category and role #
        roleMonopolyRunAdministrator = await ctx.guild.create_role(name='Monopoly Run Administrator')
        catMonopolyRun = await ctx.guild.create_category('Monopoly Run')

        # Create team roles #
        for strTeam in lisTeams:
            diRole = await ctx.guild.create_role(name=f'{strTeam}')
            lisRoles.append(diRole)  # Append role to lisRoles for setting channel permissions

        # Create announcements channel and set permissions #
        chaAnnouncements = await ctx.guild.create_text_channel('announcements', category=catMonopolyRun)
        await chaAnnouncements.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)

        # Create leaderboard channel and set permissions #
        chaLeaderBoard = await ctx.guild.create_text_channel('leaderboard', category=catMonopolyRun)
        await chaLeaderBoard.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)

        # Create properties channel and set permissions #
        chaProperties = await ctx.guild.create_text_channel('properties', category=catMonopolyRun)
        await chaProperties.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)

        # Create help channel and set permissions #
        chaHelp = await ctx.guild.create_text_channel('help', category=catMonopolyRun)
        await chaHelp.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        msg = await chaHelp.send('If you need help click the 👍 button below...')
        await msg.add_reaction('👍')

        # Allow teams to view the announcements, leaderboard, properties and help channels #
        for roleTeam in lisRoles:
            for category in ctx.message.guild.categories:
                if 'Monopoly Run' in category.name:
                    for channel in category.text_channels:
                        await channel.set_permissions(roleTeam, send_messages=False, read_messages=True, view_channel=True)

        # Create team channels and set permissions #
        for strTeam, roleTeam in zip(lisTeams, lisRoles):  # Loop through both lists at the same time
            chaChannel = await ctx.guild.create_text_channel(f'{strTeam}', category=catMonopolyRun)
            await chaChannel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
            await chaChannel.set_permissions(roleTeam, send_messages=False, read_messages=True, view_channel=True)

        # Allow monopoly run administrators to view and send messages in all channels #
        for chaChannel in catMonopolyRun.channels:
            await chaChannel.set_permissions(roleMonopolyRunAdministrator, send_messages=True, read_messages=True, view_channel=True)

        # Create guilds table in the database #
        dbcursor.execute(f"""CREATE OR REPLACE TABLE tbl_{strGuildID} (
        id varchar(6) NOT NULL PRIMARY KEY,
        money smallint(5) NOT NULL,
        current_location TEXT,
        brown1_owner set('Y','N') NOT NULL DEFAULT 'N',
        brown1_visited set('Y','N') NOT NULL DEFAULT 'N',
        brown2_owner set('Y','N') NOT NULL DEFAULT 'N',
        brown2_visited set('Y','N') NOT NULL DEFAULT 'N',
        lightblue1_owner set('Y','N') NOT NULL DEFAULT 'N',
        lightblue1_visited set('Y','N') NOT NULL DEFAULT 'N',
        lightblue2_owner set('Y','N') NOT NULL DEFAULT 'N',
        lightblue2_visited set('Y','N') NOT NULL DEFAULT 'N',
        lightblue3_owner set('Y','N') NOT NULL DEFAULT 'N',
        lightblue3_visited set('Y','N') NOT NULL DEFAULT 'N',
        pink1_owner set('Y','N') NOT NULL DEFAULT 'N',
        pink1_visited set('Y','N') NOT NULL DEFAULT 'N',
        pink2_owner set('Y','N') NOT NULL DEFAULT 'N',
        pink2_visited set('Y','N') NOT NULL DEFAULT 'N',
        pink3_owner set('Y','N') NOT NULL DEFAULT 'N',
        pink3_visited set('Y','N') NOT NULL DEFAULT 'N',
        orange1_owner set('Y','N') NOT NULL DEFAULT 'N',
        orange1_visited set('Y','N') NOT NULL DEFAULT 'N',
        orange2_owner set('Y','N') NOT NULL DEFAULT 'N',
        orange2_visited set('Y','N') NOT NULL DEFAULT 'N',
        orange3_owner set('Y','N') NOT NULL DEFAULT 'N',
        orange3_visited set('Y','N') NOT NULL DEFAULT 'N',
        black1_owner set('Y','N') NOT NULL DEFAULT 'N',
        black1_visited set('Y','N') NOT NULL DEFAULT 'N',
        black2_owner set('Y','N') NOT NULL DEFAULT 'N',
        black2_visited set('Y','N') NOT NULL DEFAULT 'N',
        black3_owner set('Y','N') NOT NULL DEFAULT 'N',
        black3_visited set('Y','N') NOT NULL DEFAULT 'N',
        black4_owner set('Y','N') NOT NULL DEFAULT 'N',
        black4_visited set('Y','N') NOT NULL DEFAULT 'N',
        red1_owner set('Y','N') NOT NULL DEFAULT 'N',
        red1_visited set('Y','N') NOT NULL DEFAULT 'N',
        red2_owner set('Y','N') NOT NULL DEFAULT 'N',
        red2_visited set('Y','N') NOT NULL DEFAULT 'N',
        red3_owner set('Y','N') NOT NULL DEFAULT 'N',
        red3_visited set('Y','N') NOT NULL DEFAULT 'N',
        yellow1_owner set('Y','N') NOT NULL DEFAULT 'N',
        yellow1_visited set('Y','N') NOT NULL DEFAULT 'N',
        yellow2_owner set('Y','N') NOT NULL DEFAULT 'N',
        yellow2_visited set('Y','N') NOT NULL DEFAULT 'N',
        yellow3_owner set('Y','N') NOT NULL DEFAULT 'N',
        yellow3_visited set('Y','N') NOT NULL DEFAULT 'N',
        green1_owner set('Y','N') NOT NULL DEFAULT 'N',
        green1_visited set('Y','N') NOT NULL DEFAULT 'N',
        green2_owner set('Y','N') NOT NULL DEFAULT 'N',
        green2_visited set('Y','N') NOT NULL DEFAULT 'N',
        green3_owner set('Y','N') NOT NULL DEFAULT 'N',
        green3_visited set('Y','N') NOT NULL DEFAULT 'N',
        darkblue1_owner set('Y','N') NOT NULL DEFAULT 'N',
        darkblue1_visited set('Y','N') NOT NULL DEFAULT 'N',
        darkblue2_owner set('Y','N') NOT NULL DEFAULT 'N',
        darkblue2_visited set('Y','N') NOT NULL DEFAULT 'N'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

        # Create records in guilds table  #
        for strTeam in lisTeams:
            dbcursor.execute(f"INSERT INTO tbl_{strGuildID} (id, money, current_location) VALUES (?, ?, ?)", (strTeam, 0, ''))

        # Create a record in tbl_guild #
        dbcursor.execute("INSERT INTO tbl_guilds (id, name, questions, teams) VALUES (?, ?, ?, ?)", (intGuildID, strGuildName, strQuestionSet, intNumberOfTeams))

        # Tell the user setup is complete #
        await ctx.send('Setup is done!')

    ##################
    # Remove Command #
    ##################

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def remove(self, ctx, blnConfirm: bool):

        # Check if blnConfirm is false #
        if blnConfirm is False:
            raise commands.BadArgument()

        # Declare some key variables #
        strGuildID = str(ctx.guild.id)

        # Check if there is anything to remove #
        dbcursor.execute("SELECT id FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisExists = dbcursor.fetchall()
        if not lisExists:
            raise MonopolyRunError.DatabaseRecordNotFound()

        # Delete all channels in the category Monopoly Run #
        for category in ctx.message.guild.categories:
            if 'Monopoly Run' in category.name:
                for channel in category.text_channels:
                    await channel.delete()
                await category.delete()

        dbcursor.execute("SELECT teams FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]
        # Declare a list of roles to try and delete #
        lisRoles = ['Monopoly Run Administrator']
        for i in range(intNumberOfTeams):
            lisRoles.append(f'team{i+1}')

        # Delete roles #
        for role in ctx.guild.roles:
            if role.name in lisRoles:
                await role.delete()

        # Drop guilds table #
        dbcursor.execute(f"DROP TABLE tbl_{strGuildID}")

        # Remove record from tbl_guild #
        dbcursor.execute("DELETE FROM tbl_guilds WHERE id = ?", (strGuildID, ))

    ####################
    # Add Team Command #
    ####################
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def add(self, ctx):

        # Declare some key variables #
        strGuildID = str(ctx.guild.id)

        # Check if there is anything to add to #
        dbcursor.execute("SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        if not lisNumberOfTeams:
            raise MonopolyRunError.DatabaseRecordNotFound()

        # Get the number of teams the guild currently has #
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]

        # Handle max number of teams #
        if intNumberOfTeams == 46:
            raise MonopolyRunError.TooManyTeams()

        # Get the Monopoly Run Category #
        catMonopolyRun = utils.get(ctx.guild.categories, name='Monopoly Run')

        # Define a variable with the new team to add #
        strNewTeamName = f'team{intNumberOfTeams + 1}'

        # Create team Role #
        roleNewTeam = await ctx.guild.create_role(name=strNewTeamName)

        # Get Monopoly Run Administrator Role #
        roleMonopolyRunAdministrator = utils.get(ctx.guild.roles, name='Monopoly Run Administrator')

        # Create team channel and set permissions  #
        chaChannel = await ctx.guild.create_text_channel(strNewTeamName, category=catMonopolyRun)
        await chaChannel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaChannel.set_permissions(roleNewTeam, send_messages=False, read_messages=True, view_channel=True)
        await chaChannel.set_permissions(roleMonopolyRunAdministrator, send_messages=True, read_messages=True, view_channel=True)

        # Set permissions on announcements, leaderboard, properties and help channel #
        chaAnnouncements = utils.get(ctx.guild.channels, name='announcements', category=catMonopolyRun)
        chaLeaderBoard = utils.get(ctx.guild.channels, name='leaderboard', category=catMonopolyRun)
        chaProperties = utils.get(ctx.guild.channels, name='properties', category=catMonopolyRun)
        chaHelp = utils.get(ctx.guild.channels, name='help', category=catMonopolyRun)

        await chaAnnouncements.set_permissions(roleNewTeam, send_messages=False, read_messages=True, view_channel=True)
        await chaLeaderBoard.set_permissions(roleNewTeam, send_messages=False, read_messages=True, view_channel=True)
        await chaProperties.set_permissions(roleNewTeam, send_messages=False, read_messages=True, view_channel=True)
        await chaHelp.set_permissions(roleNewTeam, send_messages=False, read_messages=True, view_channel=True)
        
        # Add team record to guilds table #
        dbcursor.execute(f"INSERT INTO tbl_{strGuildID} (id, money, current_location) VALUES (?, ?, ?)", (strNewTeamName, 0, ''))

        # Update number of teams in guild table #
        dbcursor.execute("UPDATE tbl_guilds SET teams = ? WHERE id = ?", (intNumberOfTeams + 1, strGuildID))

    ######################
    # Start Game Command #
    ######################
    @commands.command()
    @commands.has_role('Monopoly Run Administrator')
    async def start(self, ctx):

        # Declare some key variables #
        strGuildID = str(ctx.guild.id)
        catMonopolyRun = utils.get(ctx.guild.categories, name='Monopoly Run')

        # Check if there is anything to add to #
        dbcursor.execute("SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        if not lisNumberOfTeams:
            raise MonopolyRunError.DatabaseRecordNotFound()

        # Start UpdatePropertiesChannel Loop and UpdateLeaderBoard Loop #
        self.UpdatePropertiesChannel.start(self, ctx)
        self.UpdateLeaderBoard.start(self, ctx)

        # Get the number of teams the guild currently has #
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]

        # Declare lisTeams based on number of teams #
        lisTeams = []
        for i in range(intNumberOfTeams):
            lisTeams.append(f'team{i+1}')

        # Update send permissions on team channels #
        for strTeam in lisTeams:
            rolTeam = utils.get(ctx.guild.roles, name=f'{strTeam}')
            chaTeam = utils.get(ctx.guild.channels, name=f'{strTeam}')
            await chaTeam.set_permissions(rolTeam, send_messages=True, view_channel=True)

        # Get Announcement Channel and send a message #
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name='announcements', category_id=catMonopolyRun.id)
        await chaAnnouncementChannel.send('Game Start!')

    #####################
    # Stop Game Command #
    #####################

    @commands.command()
    @commands.has_role('Monopoly Run Administrator')
    async def stop(self, ctx):

        # Declare some key variables #
        strGuildID = str(ctx.guild.id)
        catMonopolyRun = utils.get(ctx.guild.categories, name='Monopoly Run')

        # Check if there is anything to add to #
        dbcursor.execute("SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        if not lisNumberOfTeams:
            raise MonopolyRunError.DatabaseRecordNotFound()

        claAdministration.UpdatePropertiesChannel.stop()
        claAdministration.UpdateLeaderBoard.stop()

        # Get the number of teams the guild currently has #
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]

        # Declare lisTeams based on number of teams #
        lisTeams = []
        for i in range(intNumberOfTeams):
            lisTeams.append(f'team{i+1}')

        # Update send permissions on team channels #
        for strTeam in lisTeams:
            rolTeam = utils.get(ctx.guild.roles, name=f'{strTeam}')
            chaTeam = utils.get(ctx.guild.channels, name=f'{strTeam}')
            await chaTeam.set_permissions(rolTeam, send_messages=False, view_channel=True)

        # Get Announcement Channel and send a message #
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name='announcements', category_id=catMonopolyRun.id)
        await chaAnnouncementChannel.send('Game Over!')

    #############################
    # Update Properties Channel #
    #############################
    @tasks.loop(minutes=2, count=None)
    async def UpdatePropertiesChannel(self, ctx):

        # Declare some key variables #
        strGuildID = str(ctx.guild.id)

        # Get which set of Questions the guild is using #
        dbcursor.execute("SELECT questions FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisQuestions = dbcursor.fetchall()
        tupQuestions = lisQuestions[0]
        strQuestions = tupQuestions[0]

        # Create Embeds #
        emBrownProperties = embeds.Embed(
            title='Brown Properties',
            color=Colour.from_rgb(139, 69, 19)
        )
        emLightBlueProperties = embeds.Embed(
            title='Light Blue Properties',
            color=Colour.from_rgb(135, 206, 235)
        )
        emPinkProperties = embeds.Embed(
            title='Pink Properties',
            color=Colour.from_rgb(218, 112, 214)
        )
        emOrangeProperties = embeds.Embed(
            title='Orange Properties',
            color=Colour.from_rgb(255, 165, 0)
        )
        emRedProperties = embeds.Embed(
            title='Red Properties',
            color=Colour.from_rgb(255, 0, 0)
        )
        emYellowProperties = embeds.Embed(
            title='Yellow Properties',
            color=Colour.from_rgb(255, 255, 0)
        )
        emGreenProperties = embeds.Embed(
            title='Green Properties',
            color=Colour.from_rgb(0, 179, 0)
        )
        emDarkBlueProperties = embeds.Embed(
            title='Dark Blue Properties',
            color=Colour.from_rgb(0, 0, 255)
        )
        emBlackProperties = embeds.Embed(
            title='Train Stations',
            color=Colour.from_rgb(255, 255, 255)
        )

        # Get id, value and location from database and add to the relevant embeds #
        dbcursor.execute(f"SELECT id, value, location FROM tbl_{strQuestions}")
        lisProperties = dbcursor.fetchall()
        for item in lisProperties:

            # Get owner if any #
            dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {item[0]}_owner = 'Y'")
            lisOwner = dbcursor.fetchall()
            if not lisOwner:
                strOwner = None
            else:
                tupOwner = lisOwner[0]
                strOwner = tupOwner[0]

            # Add fields to Embed #
            if re.sub('[0-9]+', '', item[0]) == 'brown':
                emBrownProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'lightblue':
                emLightBlueProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]}  \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'pink':
                emPinkProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'orange':
                emOrangeProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'red':
                emRedProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'yellow':
                emYellowProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'green':
                emGreenProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'darkblue':
                emDarkBlueProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')
            elif re.sub('[0-9]+', '', item[0]) == 'black':
                 emBlackProperties.add_field(name=item[2], value=f'ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}')

        # Get the properties channel #
        catMonopolyRun = utils.get(ctx.guild.categories, name='Monopoly Run')
        chaProperties = utils.get(ctx.guild.channels, name='properties', category_id=catMonopolyRun.id)

        # Remove last message #
        await chaProperties.purge(limit=10)

        # Send the embeds #
        await chaProperties.send(embed=emBrownProperties)
        await chaProperties.send(embed=emLightBlueProperties)
        await chaProperties.send(embed=emPinkProperties)
        await chaProperties.send(embed=emOrangeProperties)
        await chaProperties.send(embed=emBlackProperties)
        await chaProperties.send(embed=emRedProperties)
        await chaProperties.send(embed=emYellowProperties)
        await chaProperties.send(embed=emGreenProperties)
        await chaProperties.send(embed=emDarkBlueProperties)
       

    #######################
    # Update Leader Board #
    #######################
    @tasks.loop(minutes=2.1, count=None)
    async def UpdateLeaderBoard(self, ctx):

        # Declare some key variables #
        strGuildID = str(ctx.guild.id)

        # Get teams and there money ordered highest to lowest #
        dbcursor.execute(f"SELECT id, money FROM tbl_{strGuildID} ORDER BY money DESC")
        lisLeaderBoard = dbcursor.fetchall()
        emLeaderBoard = embeds.Embed(
            title='Leaderboard!',
            color=Colour.orange()
        )
        i = 1
        for item in lisLeaderBoard:

            # Add to embed #
            emLeaderBoard.add_field(name=f'{i}. {item[0]}', value=f'Money: {item[1]}', inline=False)
            i = i + 1

        # Get the properties channel #
        catMonopolyRun = utils.get(ctx.guild.categories, name='Monopoly Run')
        chaLeaderBoard = utils.get(ctx.guild.channels, name='leaderboard', category_id=catMonopolyRun.id)

        # Remove last message #
        await chaLeaderBoard.purge(limit=2)

        # Send the embed #
        await chaLeaderBoard.send(embed=emLeaderBoard)

    ##################
    # Error Handling #
    ##################
    async def cog_command_error(self, ctx, error):
        # Missing Required Argument #
        if isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.name == 'setup':
                await ctx.send(f':no_entry: Please specify both the number of teams to create and the question set! ```e.g. mr {ctx.command} 4 test```')
            elif ctx.command.name == 'remove':
                await ctx.send(f':no_entry: Please enter true to confirm removal! ```e.g. mr {ctx.command} true```')

        # Missing Permissions #
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(':no_entry: You do not have permission to use that command!')

        # Bad Argument #
        elif isinstance(error, commands.BadArgument):
            if ctx.command.name == 'setup':
                await ctx.send(f':no_entry: Please enter a valid number of teams to create! ```e.g. mr {ctx.command} 4 test```')
            elif ctx.command.name == 'remove':
                await ctx.send(f':no_entry: Please enter true to confirm removal! ```e.g. mr {ctx.command} true```')

        # Missing Role #
        elif isinstance(error, commands.MissingRole):
            await ctx.send(':no_entry: You need the Monopoly Run Administrator role to use that command!')
        # Database records not found #
        elif isinstance(error, MonopolyRunError.DatabaseRecordNotFound):
            await ctx.send(':no_entry: No database records were found for this sever! Have you run setup?')

        # Too many teams #
        elif isinstance(error, MonopolyRunError.TooManyTeams):
            if ctx.command.name == 'add':
                await ctx.send(':no_entry: You can not create any teams as you will be over the maximum allowed amount of teams!')
            else:
                await ctx.send(':no_entry: Maximum amount of teams is 46!')

        # Not enough teams #
        elif isinstance(error, MonopolyRunError.NotEnoughTeams):
            await ctx.send(':no_entry: Minimum amount of teams is 2!')

        # No Private Message #
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(':no_entry: Please use all commands in a Server (Not Direct Messages)!')

        # Any other error #
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')
