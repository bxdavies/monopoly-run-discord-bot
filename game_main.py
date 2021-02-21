##################
# Import Modules #
##################
from discord.ext import commands
from discord import utils
from database_connection import dbcursor
from logging_setup import logging
from fuzzywuzzy import fuzz
import re
import random
import asyncio

##############
# Game Class #
##############
class claGame(commands.Cog):

    ####################
    # Initialize Class #
    ####################
    def __init__(self, bot):
        self.bot = bot

        ## Define some lists to use later ##
        self.lisProperties = ['brown1','brown2','lightblue1','lightblue2','lightblue3','pink1','pink2','pink3','orange1','orange2','orange3','red1','red2','red3','yellow1','yellow2','yellow3','green1','green2','green3','darkblue1','darkblue2']
        self.lisTeamChannels = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']
        self.lisTeamRoles = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']
        self.lisLocations = ['property','community-chest','property','income-tax','property','property','chance','property','property','property','electric-company','property','property','property','property','property','community-chest','property','property','property','chance','property','property','property','property','water-works','property','go-to-jail','property','property','community-chest','property','property','chance','property','property','super-tax','go','just-visiting','free-parking']

    ##############
    # Converters #
    ##############
    print()
    ## Convert to lowercase ##
    def funToLower(strString):
        return strString.lower()

    ##################
    # Command Checks #
    ##################

    ## Check if command is being used in a team channel ##
    def funValidChannel(ctx):
        lisTeamChannels = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']
        if ctx.channel.name in lisTeamChannels:
            return True
        else:
            return False

    #################
    # Go To Command #
    #################

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def goto(self, ctx, strProperty: funToLower):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))
        roleTeam = utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles)

        ## Check if property exists ##
        if strProperty not in self.lisProperties:
            await ctx.send(':tophat: Please enter a valid property! e.g. ```&goto brown1``` For a list of properties see the properties channel!')
            return None

        ## Check if the team has an action they need to carry out ##
        dbcursor.execute(f"SELECT current_location FROM tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisCurrentLocation = dbcursor.fetchall()
        for item in lisCurrentLocation:
            if item[0] != "":
                await ctx.send(f':tophat: You need to visit or do: {item[0]}, first!')
                return None

        ## Get money and visited from the database ##
        dbcursor.execute(f"SELECT money, {strProperty}_visted FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoneyVisted = dbcursor.fetchall()
        for item in lisMoneyVisted:
            intTeamsMoney = item[0]
            strVisted = item[1]

        ## Check if the team has already visited that property ##
        if strVisted == 'Y':
            await ctx.send(':tophat: You have already answered the question for that property correctly!')
            return None

        ## Get which set of Questions the guild is using ##
        dbcursor.execute("SELECT questions FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisQuestions = dbcursor.fetchall()
        tupQuestions = lisQuestions[0]
        strQuestions = tupQuestions[0]

        ## Pick an element from the list randomly and assign it to a variable ##
        intLocation = random.randint(0, 39)
        strLocation = self.lisLocations[intLocation]
        #strLocation = "go-to-jail"

        ## Update current_location to the Location the team is at ##
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", (strLocation, strTeamName))

        ## Check Value of Random Element from list and carry out actions ##

        ### Property ###
        if strLocation == "property":
            
            print(strQuestions)
            # Get Location and Question from the Database #
            dbcursor.execute(f"SELECT location, question FROM tbl_{strQuestions} WHERE id = ?", (strProperty, ))
            lisLocationQuestion = dbcursor.fetchall()
            print(lisLocationQuestion)
            for item in lisLocationQuestion:
                strPropertyLocation = item[0]
                strQuestion = item[1]

            print(strPropertyLocation)
            # Update Database to the Location the user is now at
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", (strProperty, strTeamName))
            # Send user a message telling the the Question, Location and Property
            await ctx.send(f':question: The question for {strLocation} at {strPropertyLocation} is: {strQuestion}')

        ### Community Chest ###
        elif strLocation == "community-chest":

            # Notify the user #
            await ctx.send(':credit_card: You have a Community Chest Card! Check what it is with: ```&cch```')

        ### Chance ###
        elif strLocation == "chance":

            # Notify the user #
            await ctx.send(':bulb: You have a Chance Card! Check what it is with: ```&cha```')

        ### Income Tax ###
        elif strLocation == "income-tax":

            # Update Money in Database#
            intUpdatedMoney = intTeamsMoney - 200
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Notify the user #
            await ctx.send(':dollar: Income Tax: Paid £200!')

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

        ### Electric Company ###
        elif strLocation == "electric-company":
            await ctx.send("Not coded yet!")

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

        ### Water Works ###
        elif strLocation == "water-works":
            await ctx.send("Not coded yet!")

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

        ### Go To Jail ###
        elif strLocation == "go-to-jail":

            # Notify the user #
            await ctx.send(':closed_lock_with_key: Go to Jail!')

            # Set there team channel send messages to false #
            await ctx.channel.set_permissions(roleTeam, send_messages=False, read_messages=True)

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

            # Start Jail Loop #
            await claGame.JailLoop(self, ctx)

        ### Super Tax ###
        elif strLocation == "super-tax":

            # Update Money in Database
            intUpdatedMoney = intTeamsMoney - 75
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Notify the user #
            await ctx.send(':dollar: Luxury Tax: Paid £75!')

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

        ### Go ###
        elif strLocation == "go":

            # Update Money in Database
            intUpdatedMoney = intTeamsMoney + 200
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Notify the user #
            await ctx.send(':pushpin: You just passed GO, this means you get £200!')

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))


        ### Just Visiting ###
        elif strLocation == "just-visiting":

            # Notify the user #
            await ctx.send(':pushpin: You are at: Just Visiting! This means you have to wait 10 seconds!')

            # Set there team channel send messages to false #
            await ctx.channel.set_permissions(roleTeam, send_messages=False, read_messages=True)

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

            # Start Ten Loop #
            await claGame.TenLoop(self, ctx)

        ### Free Parking ###
        elif strLocation == "free-parking":
            # Notify the user #
            await ctx.send(':pushpin: You are at: Free Parking! This means you have to wait 10 seconds!')

            # Set there team channel send messages to false #
            await ctx.channel.set_permissions(roleTeam, send_messages=False, read_messages=True)

            # Set current_location to empty #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

            # Start Ten Loop #
            await claGame.TenLoop(self, ctx)

        ### Error ###
        else:
            logging.error(f'Unexpected error: strLocation is not valid! {strLocation}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: strLocation is not valid! {strLocation}``` ')
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

    # Error Handling #
    @goto.error
    async def goto_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(':no_entry: You need to specify the property! e.g. ```&goto brown1```')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ###########################
    # Community Chest Command #
    ###########################

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def cch(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))

        ## Check if team has a community chest card ##
        dbcursor.execute(f"SELECT current_location from tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisCurrentLocation = dbcursor.fetchall()
        for item in lisCurrentLocation:
            if item[0] != "community-chest":
                await ctx.send(':tophat: You do not have a Community Chest Card!')
                return None

        ## Get how much money the team has ##
        dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoney = dbcursor.fetchall()
        tupMoney = lisMoney[0]
        intTeamsMoney = int(tupMoney[0])

        ## Get and Set Announcement Channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)

        intCommunityChest = random.randint(1,8)

        ## Update current_location to the Square the team is at ##
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", (intCommunityChest, strTeamName))

        ### Program Error ###
        if intCommunityChest == 1:
            intUpdatedMoney = intTeamsMoney + 200
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':dollar: Program Error! Collect £200')

        ### Its your birthday ###
        elif intCommunityChest == 2:
            dbcursor.execute(f"SELECT id, money FROM tbl_{strGuildID}")
            lisTeamsMoney = dbcursor.fetchall()
            for item in lisTeamsMoney:
                if item[0] != strTeamName:
                    intUpdatedMoney = item[1] - 10
                    dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, item[0]))

            dbcursor.execute(f"SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
            lisTeams = dbcursor.fetchall()
            tupTeams = lisTeams[0]
            intTeams = tupTeams[0]
            intTeams = intTeams - 1
            intUpdatedMoney = intTeamsMoney + (intTeams * 10)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':birthday: Its your birthday! Collect £10 from each team!')

            roleMonopolyRun = utils.get(ctx.guild.roles, name="Monopoly Run")
            await chaAnnouncementChannel.send(f':birthday: {roleMonopolyRun.mention}  It is {strTeamName} birthday! You gave them a gift of £10!')

        ### Income Tax Refund ###
        elif intCommunityChest == 3:
            intUpdatedMoney = intTeamsMoney + 20
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':dollar: Income Tax Refund, Collect £20!')

        ### Inherit 100 ###
        elif intCommunityChest == 4:
            intUpdatedMoney = intTeamsMoney + 100
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':older_woman: You have inherited £100!')

        ### Hint ###
        elif intCommunityChest == 5:
            await ctx.send(':question: You get a hint!')
            #To Do

        ### Crossword Competition ###
        elif intCommunityChest == 6:
            intUpdatedMoney = intTeamsMoney + 100
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':newspaper: You have won a crossword competition, this means you get £100!')

        ### 10% from winning Team ###
        elif intCommunityChest == 8:
            dbcursor.execute(f"select id, money from tbl_{strGuildID} where money=(select max(money) from tbl_{strGuildID})")
            lisWinningTeam = dbcursor.fetchall()
            for item in lisWinningTeam:
                floUpdatedMoney = item[1] - (item[1] * 0.10)
                intUpdatedMoney = int(floUpdatedMoney)
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, item[0]))
                chaWinningTeam = utils.get(ctx.guild.channels, name=item[0])
                await chaWinningTeam.send(f"Oh no! {strTeamName} just took £{item[1] * 0.10} from you!")
                floUpdatedMoney = intTeamsMoney + (item[1] * 0.10)
                intUpdatedMoney = int(floUpdatedMoney)
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))


            await ctx.send(':trophy: Take 10% from the winning team!')


        ### Error ###
        else:
            logging.error(f'Unexpected error: intCommunityChest is not valid! {intCommunityChest}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: intCommunityChest is not valid! {intCommunityChest}``` ')

        ## Update the current square to empty ##
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

    # Error Handling #
    @cch.error
    async def cch_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ##################
    # Chance Command #
    ##################

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def cha(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))
        roleTeam = utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles)

        ## Check if team has a chance card ##
        dbcursor.execute(f"SELECT current_location from tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisCurrentLocation = dbcursor.fetchall()
        for item in lisCurrentLocation:
            if item[0] != "chance":
                await ctx.send(':tophat: You do not have a Chance Card!')
                return None

        ## Get how much money the team has ##
        dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoney = dbcursor.fetchall()
        tupMoney = lisMoney[0]
        intTeamsMoney = int(tupMoney[0])

        ## Get and Set Announcement Channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)

        intChance = random.randint(1, 8)

        ## Update current_location to the Square the team is at ##
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", (intChance, strTeamName))

        ### Chair of the Game ###
        if intChance == 1:
            dbcursor.execute(f"SELECT id, money FROM tbl_{strGuildID}")
            lisTeamsMoney = dbcursor.fetchall()
            for item in lisTeamsMoney:
                if item[0] != strTeamName:
                    intUpdatedMoney = item[1] + 50
                    dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, item[0]))

            dbcursor.execute(f"SELECT teams from tbl_guilds WHERE id = ?", (strGuildID, ))
            lisTeams = dbcursor.fetchall()
            tupTeams = lisTeams[0]
            intTeams = tupTeams[0]
            intTeams = intTeams - 1
            intUpdatedMoney = intTeamsMoney - (intTeams * 50)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':chair: You have been elected Chair of the Game, this means you pay each player £50')
            await chaAnnouncementChannel.send(f':chair: {strTeamName} has been Chosen as the Chair of the Game, which means everyone gets £50!')

        ### Go to Jail ###
        elif intChance == 2:
            ctx.send(':closed_lock_with_key: Go to Jail!, this means you can not do anything for 30 seconds')
            await ctx.channel.set_permissions(roleTeam, send_messages=False, read_messages=True)
            await claGame.JailLoop(ctx)

        ### School Fees ###
        elif intChance == 3:
            await ctx.send(':school: School Fees, Pay £50!')
            intUpdatedMoney = intTeamsMoney - 50
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

        ### Pay losing team ###
        elif intChance == 4:
            dbcursor.execute(f"SELECT id, money FROM tbl_{strGuildID} WHERE money=(SELECT MIN(money) FROM tbl_{strGuildID})")
            lisLosingTeam = dbcursor.fetchall()
            for item in lisLosingTeam:
                intUpdatedMoney = item[1] + 100
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, item[0]))
                chaLosingTeam = utils.get(ctx.guild.channels, name=item[0])
                await chaLosingTeam.send(f':dollar: Good News! {strTeamName} just paid you £100!')

            intUpdatedMoney = intTeamsMoney - 100
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':dollar: Pay the losing team £100')

        ### Pay winning team ###
        elif intChance == 5:
            dbcursor.execute(f"SELECT id, money FROM tbl_{strGuildID} WHERE money=(SELECT MAX(money) FROM tbl_{strGuildID})")
            lisWinningTeam = dbcursor.fetchall()
            for item in lisWinningTeam:
                intUpdatedMoney = item[1] + 50
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, item[0]))
                chaWinningTeam = utils.get(ctx.guild.channels, name=item[0])
                await chaWinningTeam.send(f':dollar: Good News! {strTeamName} just paid you £50!')

            intUpdatedMoney = intTeamsMoney - 50
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(":dollar: Pay the winning team £50")

        elif intChance == 6:
            # Not sure yet
            await ctx.send("Not coded yet!")

        ### Pay Double Rent ###
        elif intChance == 7:
            await ctx.send(':homes: Pay double rent on the next property you go to!')

        ### Wait one Minute ###
        elif intChance == 8:
            await ctx.send(':timer: Wait one minute')
            await ctx.channel.set_permissions(roleTeam, send_messages=False, read_messages=True)
            await claGame.OneLoop(self, ctx)

        ### Error ###
        else:
            logging.error(f'Unexpected error: intChance is not valid! {intChance}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: intChance is not valid! {intChance}``` ')


        ## Update the current square to empty ##
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

    # Error Handling #
    @cha.error
    async def cha_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ##################
    # Answer Command #
    ##################

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def answ(self, ctx, *, strAnswer):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))

        ## Get teams current location ##
        dbcursor.execute(f"SELECT current_location FROM tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisCurrentSquare = dbcursor.fetchall()
        tupCurrentSquare = lisCurrentSquare[0]
        strCurrentSquare = tupCurrentSquare[0]

        ## Check if team has said they are going to visit the property ##
        if strCurrentSquare not in self.lisProperties:
            print(strCurrentSquare)
            if strCurrentSquare == '':
                await ctx.send(':tophat: You need to use goto first to tell the game where your going! ```&goto brown1```')
                return None
            else:
                await ctx.send(f':tophat: You need to visit or do: {strCurrentSquare}, first!')
                return None

        ## Update the current square to empty ##
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", ("", strTeamName))

        ## Set property to location ##
        strProperty = strCurrentSquare


        ## Get teams money and if they have visited this property from the database ##
        dbcursor.execute(f"SELECT money, {strProperty}_visted FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoneyVisted = dbcursor.fetchall()
        for item in lisMoneyVisted:
            intTeamsMoney = item[0]
            strVisted = item[1]

        ## Check if a team owns the property ##
        dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {strProperty}_owner = 'Y'")
        lisOwner = dbcursor.fetchall()
        if not lisOwner:
            strOwner = None
        else:
            tupOwner = lisOwner[0]
            strOwner = tupOwner[0]

        ## Get which set of Questions the guild is using ##
        dbcursor.execute("SELECT questions FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisQuestions = dbcursor.fetchall()
        tupQuestions = lisQuestions[0]
        strQuestions = tupQuestions[0]

        ## Get answer and value from database ##
        dbcursor.execute(f"SELECT answer, value FROM tbl_{strQuestions} WHERE id = ?", (strProperty, ))
        lisOwnerAnswer = dbcursor.fetchall()
        for item in lisOwnerAnswer:
            strCorrectAnswers = item[0]
            intValue = item[1]
        strValue = str(intValue)

        ## Check if a set of properties is owned by one team ##
        lisPropertiesToSelect = [i for i in self.lisProperties if i.startswith(re.sub('[0-9]+', '', strProperty))]
        intNumberofPropertiesToSelect = len(lisPropertiesToSelect)
        if intNumberofPropertiesToSelect == 2:
            dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {lisPropertiesToSelect[0]}_owner = 'Y' and {lisPropertiesToSelect[1]}_owner = 'Y'")
            lisPropertiesInSet = dbcursor.fetchall()
            if not lisPropertiesInSet:
                blnDoubleRent = False
            else:
                blnDoubleRent = True
        elif intNumberofPropertiesToSelect == 3:
            dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {lisPropertiesToSelect[0]}_owner = 'Y' and {lisPropertiesToSelect[1]}_owner = 'Y' and {lisPropertiesToSelect[2]}_owner = 'Y'", ())
            lisPropertiesInSet = dbcursor.fetchall()
            if not lisPropertiesInSet:
                blnDoubleRent = False
            else:
                blnDoubleRent = True
        elif intNumberofPropertiesToSelect == 4:
            dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {lisPropertiesToSelect[0]}_owner = 'Y' and {lisPropertiesToSelect[1]}_owner = 'Y' and {lisPropertiesToSelect[2]}_owner = 'Y' and {lisPropertiesToSelect[3]}_owner = 'Y'", ())
            lisPropertiesInSet = dbcursor.fetchall()
            if not lisPropertiesInSet:
                blnDoubleRent = False
            else:
                blnDoubleRent = True

        ## Check if answer is correct ##
        lisCorrectAnswers = strCorrectAnswers.split('-')
        for item in lisCorrectAnswers:

            # Convert to lowercase and remove spaces
            strCorrectAnswer = item.lower()
            strCorrectAnswer = re.sub('\s+', '', strCorrectAnswer)

            strAnswer = strAnswer.lower()
            strAnswer = re.sub('\s+', '', strAnswer)
            print(strCorrectAnswer, strAnswer)
            # Use fuzzy-wuzzy to compare the users answer with the correct answer
            intPartialRatio = fuzz.partial_ratio(strCorrectAnswer, strAnswer)
            intTokenSetRatio = fuzz.token_set_ratio(strCorrectAnswer, strAnswer)


            if intPartialRatio >= 80 or intTokenSetRatio >= 80:
                blnAnswerCorrect = True
            else:
                blnAnswerCorrect = False

        ## Check if team can afford
        if blnDoubleRent == True:
            if intTeamsMoney >= intValue * 2:
                blnAfford = True
            else:
                blnAfford = False
        elif blnDoubleRent == False:
            if intTeamsMoney >= intValue:
                blnAfford = True
            else:
                blnAfford = False
        else:
            logging.error(f'Unexpected error: intTeamsMoney is not valid! {intTeamsMoney}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: intTeamsMoney is not valid! {intTeamsMoney}``` ')


         ## Check all the information collected above against the users input ##

        ### Answer is correct and property is not owned ###
        if blnAnswerCorrect == True and strOwner == None:
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visted = 'Y' WHERE id = ?", (strTeamName, ))
            # Update teams money
            intUpdatedMoney = intTeamsMoney + intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':white_check_mark: This property is also available to buy!')

        ### Answer is correct and property is owned and owner has a group of properties so pay double rent ###

        elif blnAnswerCorrect == True and blnAfford == True and blnDoubleRent == True:
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visted = 'Y' WHERE id = ?", (strTeamName, ))
            # Update teams money
            intUpdatedMoney = intTeamsMoney - (intValue * 2)
            intUpdatedMoney = intUpdatedMoney + (intValue / 2)
            strValue = str(intValue * 2)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            # Update owners money
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f'{strTeamName} just paid £{intValue * 2} on {strProperty}!')
            intUpdatedMoney = intTeamsMoney + (intValue * 2)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))
            await ctx.send(f':white_check_mark: However since: {strOwner} already owns that property and the other properties in the same group you paid: £{strValue} in rent!')

        ### Answer is correct and property is owned so pay rent ###
        elif blnAnswerCorrect == True and blnAfford == True:
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visted = 'Y' WHERE id = ?", (strTeamName, ))
            # Update teams money
            intUpdatedMoney = intTeamsMoney - (intValue / 2)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            # Update owners money
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f'{strTeamName} just paid £{intValue} on {strProperty}!')
            intUpdatedMoney = intTeamsMoney + intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))
            await ctx.send(f':white_check_mark: However since: {strOwner} already owns that property you paid: £{strValue} in rent!')

        ### Answer is correct however the team can not afford to pay the rent ##
        elif blnAfford == False:
            await ctx.send(':tophat: Answer is correct however you can not afford the rent on that property!')

        ### Answer is incorrect ###
        elif blnAnswerCorrect == False:
            if intPartialRatio > intTokenSetRatio:
                await ctx.send(f':negative_squared_cross_mark: Try again! You were {intPartialRatio}% correct!')
            else:
                await ctx.send(f':negative_squared_cross_mark: Try again! You were {intTokenSetRatio}% correct!')
        else:
            logging.error(f'Unexpected error: Answer, Correct Answer, Answer Correct, Owner, Double Rent, Afford is not valid! {strAnswer, strCorrectAnswer, blnAnswerCorrect, strOwner, blnDoubleRent, blnAfford}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: Answer, Correct Answer, Answer Correct, Owner, Double Rent, Afford is not valid! {strAnswer, strCorrectAnswer, blnAnswerCorrect, strOwner, blnDoubleRent, blnAfford}``` ')

    # Error Handling #
    @answ.error
    async def answ_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':no_entry:  Please specify the answer!  ```e.g. &answ two cats and a dog```')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ###############
    # Own Command #
    ###############

    # Command Handling
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def own(self, ctx, strProperty: funToLower):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))

        # Check if property exits
        if strProperty not in self.lisProperties: 
            await ctx.send(':tophat: Please enter a valid property! e.g. ```&own brown1``` For a list of properties see the properties channel!')
            return None

        # Check if a team owns the property 
        dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {strProperty}_owner = 'Y'")
        lisOwner = dbcursor.fetchall()
        if not lisOwner:
            strOwner = None
        else:
            tupOwner = lisOwner[0]
            strOwner = tupOwner[0]
            await ctx.send(f':tophat: {strOwner} already owns that property!')
            return None

    
        ## Get money and visited from the database ##
        dbcursor.execute(f"SELECT money, {strProperty}_visted FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoneyVisted = dbcursor.fetchall()
        for item in lisMoneyVisted:
            intTeamsMoney = item[0]
            strVisted = item[1]

        ## Check if the team has visited that property ##
        if strVisted == 'N':
            await ctx.send(':tophat: You have not answered the question for that property correctly. Please answer the question correctly and try again!')
            return None
        
        ## Get which set of Questions the guild is using ##
        dbcursor.execute("SELECT questions FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisQuestions = dbcursor.fetchall()
        tupQuestions = lisQuestions[0]
        strQuestions = tupQuestions[0]

        ## Get property value from database ##
        dbcursor.execute(f"SELECT value FROM tbl_{strQuestions} WHERE id = ?", (strProperty, ))
        lisValue = dbcursor.fetchall()
        tupValue = lisValue[0]
        intValue = int(tupValue[0])

        ## Get and Set Announcement Channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)

        # Checks
        print(intTeamsMoney - intValue)
        if intTeamsMoney - intValue < 0:
            await ctx.send(':tophat: You can not afford that property!')
        else:
            await ctx.send(f':house: You have brought: {strProperty} for £{intValue}!')
            dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
            lisMoney = dbcursor.fetchall()
            tupMoney = lisMoney[0]
            intTeamsMoney = int(tupMoney[0])
            intUpdatedMoney = intTeamsMoney - intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ?, {strProperty}_owner = 'Y' WHERE id = ?", (intUpdatedMoney, strTeamName))
            await chaAnnouncementChannel.send(f':house: {strTeamName} now owns {strProperty}!')
    
    # Error Handling #
    @own.error
    async def own_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':no_entry: Please specify the property ```e.g. &own brown1```')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    #################
    # Money Command #
    #################

    # Command Handling 
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def money(self, ctx):
        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))

        dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?", (strTeamName ,))
        lisMoney = dbcursor.fetchall()
        tupMoney = lisMoney[0]
        intMoney = tupMoney[0]

        await ctx.send(f'You have £{intMoney}')

    # Error Handling #
    @money.error
    async def money_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')

    ##########################
    # Property Owner Command #
    ##########################

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def owner(self, ctx, strProperty: funToLower):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)

        ## Check if property exists ##
        if strProperty not in self.lisProperties:
            await ctx.send(':tophat: Please enter a valid property! e.g. ```&owner brown1``` For a list of properties see the properties channel!')
            return None

        ## Check if a team owns the property ##
        dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {strProperty}_owner = 'Y'")
        lisOwner = dbcursor.fetchall()
        if not lisOwner:
            await ctx.send(f'{strProperty} is not owned by anyone!')
        else:
            tupOwner = lisOwner[0]
            strOwner = tupOwner[0]
            await ctx.send(f'{strProperty} is owned by {strOwner}!')

    #########
    # Loops #
    #########

    async def OneLoop(self, ctx):
        roleTeam = utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles)
        await asyncio.sleep(60)
        await ctx.channel.set_permissions(roleTeam, send_messages=True, read_messages=True)
        await ctx.send("You can now continue")

    async def JailLoop(self, ctx):
        roleTeam = utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles)
        await asyncio.sleep(30)
        await ctx.channel.set_permissions(roleTeam, send_messages=True, read_messages=True)
        await ctx.send("You have now left Jail!")

    async def TenLoop(self, ctx):
        roleTeam = utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles)
        await asyncio.sleep(10)
        await ctx.channel.set_permissions(roleTeam, send_messages=True, read_messages=True)
        await ctx.send("You can now continue")
