##################
# Import Modules #
##################
from discord.ext import commands, tasks
from discord import utils, embeds, Colour
from database_connection import dbcursor
from logging_setup import logging
import re

###############
# Setup Class #
###############
class claSetup(commands.Cog):

    ####################
    # Initialize Class #
    ####################
    def __init__(self, bot):
        self.bot = bot
        self.UpdatePropertiesChannel = claSetup.UpdatePropertiesChannel
        self.UpdateLeaderBoard = claSetup.UpdateLeaderBoard

    #################
    # Setup Command #
    #################

    # Command Handling #
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx, intNumberOfTeams: int, strQuestionSet):

        ## Declare some variables for later ##
        strGuildID = str(ctx.guild.id)
        strGuildName = str(ctx.guild.name)
        intGuildID = int(ctx.guild.id)
        lisRoles = []

        ## Check if guild is already setup ##
        dbcursor.execute("SELECT id FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisExists = dbcursor.fetchall()
        for item in lisExists:
            if intGuildID == item[0]:
                await ctx.send(':no_entry: You have already run setup!')
                return None

        ## Check Question set exists ##
        dbcursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE ?", (f'tbl_{strQuestionSet}', ))
        lisQuestionSet = dbcursor.fetchall()
        if not lisQuestionSet:
            await ctx.send(':no_entry: That question set was not found!')
            return None

        ## Declare lisTeams based on user input ##
        if intNumberOfTeams <= 4: # Can not create more than 4 teams
            intNumberOfTeams = 4
            lisTeams = ['team1', 'team2', 'team3', 'team4']
        elif intNumberOfTeams == 5:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5']
        elif intNumberOfTeams == 6:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6']
        elif intNumberOfTeams == 7:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7']
        elif intNumberOfTeams == 8:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8']
        elif intNumberOfTeams >= 9: # Can not create more than 9 teams
            intNumberOfTeams = 9
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']

        ## Create Monopoly Run category and role ##
        roleMonopolyRun = await ctx.guild.create_role(name='Monopoly Run')
        catMonopolyRun = await ctx.guild.create_category('Monopoly Run')

        ## Create team roles ##
        for strTeam in lisTeams:
            diRole = await ctx.guild.create_role(name=f"{strTeam}")
            lisRoles.append(diRole) # Append role to lisRoles for setting channel permissions

        ## Create announcements channel and set permissions ##
        chaAnnouncements = await ctx.guild.create_text_channel('announcements', category=catMonopolyRun)
        await chaAnnouncements.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaAnnouncements.set_permissions(roleMonopolyRun, send_messages=False, read_messages=True)

        ## Create leaderboard channel and set permissions ##
        chaLeaderBoard = await ctx.guild.create_text_channel('leaderboard', category=catMonopolyRun)
        await chaLeaderBoard.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaLeaderBoard.set_permissions(roleMonopolyRun, send_messages=False, read_messages=True)

        ## Create properties channel and set permissions ##
        chaProperties = await ctx.guild.create_text_channel('properties', category=catMonopolyRun)
        await chaProperties.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaProperties.set_permissions(roleMonopolyRun, send_messages=False, read_messages=True)

        ## Create How to play channel and set permissions ##
        chaHowToPlay = await ctx.guild.create_text_channel('HowToPlay', category=catMonopolyRun)
        await chaHowToPlay.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaHowToPlay.set_permissions(roleMonopolyRun, send_messages=False, read_messages=True)

        ## Create auction channel and set permissions ##
        chaAuction = await ctx.guild.create_text_channel('Auction', category=catMonopolyRun)
        await chaAuction.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaAuction.set_permissions(roleMonopolyRun, send_messages=False, read_messages=True)

        ## Create team channels and set permissions ##
        for strTeam, strRole in zip(lisTeams, lisRoles): # Loop through both lists at the same time
            chaChannel = await ctx.guild.create_text_channel(f"{strTeam}", category=catMonopolyRun)
            await chaChannel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
            await chaChannel.set_permissions(strRole, send_messages=False, read_messages=True, view_channel=True)

        ## Create guilds table in the database ##
        dbcursor.execute(f"""CREATE OR REPLACE TABLE tbl_{strGuildID} (
        id varchar(5) NOT NULL PRIMARY KEY,
        money smallint(5) NOT NULL,
        current_location TEXT,
        brown1_owner set('Y','N') NOT NULL DEFAULT 'N',
        brown1_visted set('Y','N') NOT NULL DEFAULT 'N',
        brown2_owner set('Y','N') NOT NULL DEFAULT 'N',
        brown2_visted set('Y','N') NOT NULL DEFAULT 'N',
        lightblue1_owner set('Y','N') NOT NULL DEFAULT 'N',
        lightblue1_visted set('Y','N') NOT NULL DEFAULT 'N',
        lightblue2_owner set('Y','N') NOT NULL DEFAULT 'N',
        lightblue2_visted set('Y','N') NOT NULL DEFAULT 'N',
        lightblue3_owner set('Y','N') NOT NULL DEFAULT 'N',
        lightblue3_visted set('Y','N') NOT NULL DEFAULT 'N',
        pink1_owner set('Y','N') NOT NULL DEFAULT 'N',
        pink1_visted set('Y','N') NOT NULL DEFAULT 'N',
        pink2_owner set('Y','N') NOT NULL DEFAULT 'N',
        pink2_visted set('Y','N') NOT NULL DEFAULT 'N',
        pink3_owner set('Y','N') NOT NULL DEFAULT 'N',
        pink3_visted set('Y','N') NOT NULL DEFAULT 'N',
        orange1_owner set('Y','N') NOT NULL DEFAULT 'N',
        orange1_visted set('Y','N') NOT NULL DEFAULT 'N',
        orange2_owner set('Y','N') NOT NULL DEFAULT 'N',
        orange2_visted set('Y','N') NOT NULL DEFAULT 'N',
        orange3_owner set('Y','N') NOT NULL DEFAULT 'N',
        orange3_visted set('Y','N') NOT NULL DEFAULT 'N',
        red1_owner set('Y','N') NOT NULL DEFAULT 'N',
        red1_visted set('Y','N') NOT NULL DEFAULT 'N',
        red2_owner set('Y','N') NOT NULL DEFAULT 'N',
        red2_visted set('Y','N') NOT NULL DEFAULT 'N',
        red3_owner set('Y','N') NOT NULL DEFAULT 'N',
        red3_visted set('Y','N') NOT NULL DEFAULT 'N',
        yellow1_owner set('Y','N') NOT NULL DEFAULT 'N',
        yellow1_visted set('Y','N') NOT NULL DEFAULT 'N',
        yellow2_owner set('Y','N') NOT NULL DEFAULT 'N',
        yellow2_visted set('Y','N') NOT NULL DEFAULT 'N',
        yellow3_owner set('Y','N') NOT NULL DEFAULT 'N',
        yellow3_visted set('Y','N') NOT NULL DEFAULT 'N',
        green1_owner set('Y','N') NOT NULL DEFAULT 'N',
        green1_visted set('Y','N') NOT NULL DEFAULT 'N',
        green2_owner set('Y','N') NOT NULL DEFAULT 'N',
        green2_visted set('Y','N') NOT NULL DEFAULT 'N',
        green3_owner set('Y','N') NOT NULL DEFAULT 'N',
        green3_visted set('Y','N') NOT NULL DEFAULT 'N',
        darkblue1_owner set('Y','N') NOT NULL DEFAULT 'N',
        darkblue1_visted set('Y','N') NOT NULL DEFAULT 'N',
        darkblue2_owner set('Y','N') NOT NULL DEFAULT 'N',
        darkblue2_visted set('Y','N') NOT NULL DEFAULT 'N'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")

        ## Create records in guilds table  ##
        for strTeam in lisTeams:
            dbcursor.execute(f"INSERT INTO tbl_{strGuildID} (id, money, current_location) VALUES (?, ?, ?)", (strTeam, 1500, ''))

        ## Create a record in tbl_guild ##
        dbcursor.execute("INSERT INTO tbl_guilds (id, name, questions, teams) VALUES (?, ?, ?, ?)", (intGuildID, strGuildName, strQuestionSet ,intNumberOfTeams))

        ## Tell the user setup is complete ##
        await ctx.send('Setup is done!')

    # Error handling #
    @setup.error
    async def setup_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':no_entry: Please specify both the number of teams to create and the question set! ```e.g. &setup 4 test```')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(':no_entry: You do not have permission to use that command!')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(':no_entry: Please enter a valid number of teams to create! ```e.g. &setup 4 test```')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ##################
    # Remove Command #
    ##################

    # Command Handling #
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def remove(self, ctx, blnConfirm: bool):

        ## Check if blnConfirm is false ##
        if blnConfirm == False:
            await ctx.send(':no_entry: Please specify true to confirm! ```e.g. &remove true```')
            return None

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)

        ## Check if there is anything to remove ##
        dbcursor.execute("SELECT id FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisExists = dbcursor.fetchall()
        if not lisExists:
            await ctx.send(':no_entry: No database records exist for this guild or server!')
            return None

        ## Delete all channels in the category Monopoly Run ##
        for category in ctx.message.guild.categories:
            if "Monopoly Run" in category.name:
                for channel in category.text_channels:
                    await channel.delete()
                await category.delete()

        ## Declare a list of roles to try and delete ##
        lisRoles = ['Monopoly Run', 'team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']

        ## Delete roles ##
        for role in ctx.guild.roles:
            if role.name in lisRoles:
                await role.delete()

        ## Drop guilds table ##
        dbcursor.execute(f"DROP TABLE tbl_{strGuildID}")

        ## Remove record from tbl_guild ##
        dbcursor.execute("DELETE FROM tbl_guilds WHERE id = ?", (strGuildID, ))

    # Error Handling #
    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':no_entry: Please specify true or false to confirm! ```e.g. &remove true```')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(':no_entry: You do not have permission to use that command!')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(':no_entry: Please specify true or false to confirm! ```e.g. &remove true```')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ####################
    # Add Team Command #
    ####################

    # Command Handling #
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def add(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)

        ## Check if there is anything to add to ##
        dbcursor.execute(f"SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        if not lisNumberOfTeams:
            await ctx.send(':no_entry: No database records exist for this guild or server!')
            return None

        ## Get the number of teams the guild currently has ##
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]
        intUpdatedNumberOfTeams = intNumberOfTeams

        ## Check if its above 10 ##
        if intUpdatedNumberOfTeams + 1 == 10:
            await ctx.send(':no_entry: Max number of teams is 9!')
            return None

        ## Get the Monopoly Run Category ##
        for category in ctx.guild.categories:
            if "Monopoly Run" in category.name:
                catMonopolyRun = category

        ## Declare a list of teams ##
        lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']

        ## Create team Role ##
        rolTeam = await ctx.guild.create_role(name=lisTeams[intUpdatedNumberOfTeams])

        ## Create team channel and set permissions  ##
        chaChannel = await ctx.guild.create_text_channel(lisTeams[intUpdatedNumberOfTeams], category=catMonopolyRun)
        await chaChannel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False)
        await chaChannel.set_permissions(rolTeam, send_messages=False, read_messages=True, view_channel=True)

        ## Add team record to guilds table ##
        dbcursor.execute(f"INSERT INTO tbl_{strGuildID} (id, money, current_location) VALUES (?, ?, ?)", (lisTeams[intUpdatedNumberOfTeams], 1500, ''))

        ## Update number of teams in guild table ##
        dbcursor.execute(f"UPDATE tbl_guilds SET teams = ? WHERE id = ?", (intUpdatedNumberOfTeams + 1, strGuildID))

    # Error Handling #
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(':no_entry: You do not have permission to use that command!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ######################
    # Start Game Command #
    ######################

    # Command Handling #
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def start(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")

        ## Check if there is anything to add to ##
        dbcursor.execute(f"SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        if not lisNumberOfTeams:
            await ctx.send(':no_entry: No database records exist for this guild or server!')
            return None

        ## Start UpdatePropertiesChannel Loop and UpdateLeaderBoard Loop ##
        self.UpdatePropertiesChannel.start(self, ctx)
        self.UpdateLeaderBoard.start(self, ctx)

        ## Get the number of teams the guild currently has ##
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]

        ## Create a list of teams depending on how many teams the guild currently has ##
        if intNumberOfTeams <= 4: # Can not create more than 4 teams
            intNumberOfTeams = 4
            lisTeams = ['team1', 'team2', 'team3', 'team4']
        elif intNumberOfTeams == 5:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5']
        elif intNumberOfTeams == 6:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6']
        elif intNumberOfTeams == 7:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7']
        elif intNumberOfTeams == 8:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8']
        elif intNumberOfTeams >= 9: # Can not create more than 9 teams
            intNumberOfTeams = 9
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']

        ## Update send permissions on team channels ##
        for strTeam in lisTeams:
            rolTeam = utils.get(ctx.guild.roles, name=f"{strTeam}")
            chaTeam = utils.get(ctx.guild.channels, name=f"{strTeam}")
            await chaTeam.set_permissions(rolTeam, send_messages=True, view_channel=True)

        ## Update Auction Channel ##
        roleMonopolyRun = utils.get(ctx.guild.roles, name="Monopoly Run")
        chaAuctionChannel = utils.get(ctx.guild.channels, name="auction", category_id=catMonopolyRun.id)
        await chaAuctionChannel.set_permissions(roleMonopolyRun, send_messages=True, view_channel=True)

        ## Get Announcement Channel and send a message ##
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)
        await chaAnnouncementChannel.send('Game Start!')

    # Error Handling #
    @start.error
    async def start_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(':no_entry: You do not have permission to use that command!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ####################
    # End Game Command #
    ####################

    # Command Handling #
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def end(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")

        ## Check if there is anything to add to ##
        dbcursor.execute(f"SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
        lisNumberOfTeams = dbcursor.fetchall()
        if not lisNumberOfTeams:
            await ctx.send(':no_entry: No database records exist for this guild or server!')
            return None

        claSetup.UpdatePropertiesChannel.stop()
        claSetup.UpdateLeaderBoard.stop()
        
        ## Get the number of teams the guild currently has ##
        tupNumberOfTeams = lisNumberOfTeams[0]
        intNumberOfTeams = tupNumberOfTeams[0]

        ## Create a list of teams depending on how many teams the guild currently has ##
        if intNumberOfTeams <= 4: # Can not create more than 4 teams
            intNumberOfTeams = 4
            lisTeams = ['team1', 'team2', 'team3', 'team4']
        elif intNumberOfTeams == 5:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5']
        elif intNumberOfTeams == 6:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6']
        elif intNumberOfTeams == 7:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7']
        elif intNumberOfTeams == 8:
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8']
        elif intNumberOfTeams >= 9: # Can not create more than 9 teams
            intNumberOfTeams = 9
            lisTeams = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']

        ## Update send permissions on team channels ##
        for strTeam in lisTeams:
            rolTeam = utils.get(ctx.guild.roles, name=f"{strTeam}")
            chaTeam = utils.get(ctx.guild.channels, name=f"{strTeam}")
            await chaTeam.set_permissions(rolTeam, send_messages=False)

        ## Update Auction Channel ##
        roleMonopolyRun = utils.get(ctx.guild.roles, name="Monopoly Run")
        chaAuctionChannel = utils.get(ctx.guild.channels, name="auction", category_id=catMonopolyRun.id)
        await chaAuctionChannel.set_permissions(roleMonopolyRun, send_messages=False)

        ## Get Announcement Channel and send a message ##
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)
        await chaAnnouncementChannel.send(f'Game Over!')

    # Error Handling #
    @end.error
    async def end_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(':no_entry: You do not have permission to use that command!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    #############################
    # Update Properties Channel #
    #############################
    @tasks.loop(minutes=2, count=None)
    async def UpdatePropertiesChannel(self, ctx):

        # Declare some key variables ##
        strGuildID = str(ctx.guild.id)

        ## Get which set of Questions the guild is using ##
        dbcursor.execute("SELECT questions FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisQuestions = dbcursor.fetchall()
        tupQuestions = lisQuestions[0]
        strQuestions = tupQuestions[0]

        ## Create Embeds ##
        emBrownProperties = embeds.Embed(title = 'Brown Properties', color=Colour.from_rgb(139, 69, 19))
        emLightBlueProperties = embeds.Embed(title = 'Light Blue Properties', color=Colour.from_rgb(135, 206, 235))
        emPinkProperties = embeds.Embed(title = 'Pink Properties', color=Colour.from_rgb(218, 112, 214))
        emOrangeProperties = embeds.Embed(title = 'Orange Properties', color=Colour.from_rgb(255, 165, 0))
        emRedProperties = embeds.Embed(title = 'Red Properties', color=Colour.from_rgb(255, 0, 0))
        emYellowProperties = embeds.Embed(title = 'Yellow Properties', color=Colour.from_rgb(255, 255, 0))
        emGreenProperties = embeds.Embed(title = 'Green Properties', color=Colour.from_rgb(0, 179, 0))
        emDarkBlueProperties = embeds.Embed(title = 'Dark Blue Properties', color=Colour.from_rgb(0, 0, 255))

        ## Get id, value and location from database and add to the relevant embeds ##
        dbcursor.execute(f"SELECT id, value, location FROM tbl_{strQuestions}")
        lisProperties = dbcursor.fetchall()
        for item in lisProperties:

            ## Get owner if any ##
            dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {item[0]}_owner = 'Y'")
            lisOwner = dbcursor.fetchall()
            if not lisOwner:
                strOwner = None
            else:
                tupOwner = lisOwner[0]
                strOwner = tupOwner[0]

            ## Add fields to Embed ##
            if re.sub('[0-9]+', '', item[0]) == "brown":
                emBrownProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "lightblue":
                emLightBlueProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]}  \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "pink":
                emPinkProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "orange":
                emOrangeProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "red":
                emRedProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "yellow":
                emYellowProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "green":
                emGreenProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")
            elif re.sub('[0-9]+', '', item[0]) == "darkblue":
                emDarkBlueProperties.add_field(name=item[2], value=f"ID: {item[0]} \n Value: {item[1]} \n Owner: {strOwner}")

        ## Get the properties channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaProperties = utils.get(ctx.guild.channels, name="properties", category_id=catMonopolyRun.id)

        ## Remove last message ##
        await chaProperties.purge(limit=10)

        ## Send the embeds ##
        await chaProperties.send(embed = emBrownProperties)
        await chaProperties.send(embed = emLightBlueProperties)
        await chaProperties.send(embed = emPinkProperties)
        await chaProperties.send(embed = emOrangeProperties)
        await chaProperties.send(embed = emRedProperties)
        await chaProperties.send(embed = emYellowProperties)
        await chaProperties.send(embed = emGreenProperties)
        await chaProperties.send(embed = emDarkBlueProperties)

    #######################
    # Update Leader Board #
    #######################
    @tasks.loop(minutes=2.1, count=None)
    async def UpdateLeaderBoard(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)

        ## Get teams and there money ordered highest to lowest ##
        dbcursor.execute(f"SELECT id, money FROM tbl_{strGuildID} ORDER BY money DESC")
        lisLeaderBoard = dbcursor.fetchall()
        emLeaderBoard = embeds.Embed(title = 'Leaderboard!', color=Colour.orange())
        i = 1
        for item in lisLeaderBoard:

            # Add to embed #
            emLeaderBoard.add_field(name=f"{i}. {item[0]}", value=f"Money: {item[1]}", inline=False)
            i = i + 1

        ## Get the properties channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaLeaderBoard = utils.get(ctx.guild.channels, name="leaderboard", category_id=catMonopolyRun.id)

        ## Remove last message ##
        await chaLeaderBoard.purge(limit=2)

        ## Send the embed ##
        await chaLeaderBoard.send(embed = emLeaderBoard)
