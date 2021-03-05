##################
# Import Modules #
##################
from discord.ext import commands
from discord import utils
from database_connection import dbcursor
from logging_setup import logging
from fuzzywuzzy import fuzz
import re
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

    ##############
    # Converters #
    ##############

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

        # Get Location and Question from the Database #
        dbcursor.execute(f"SELECT location, question FROM tbl_{strQuestions} WHERE id = ?", (strProperty, ))
        lisLocationQuestion = dbcursor.fetchall()
        for item in lisLocationQuestion:
            strPropertyLocation = item[0]
            strQuestion = item[1]

        # Update Database to the Location the user is now at
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", (strProperty, strTeamName))

        # Send user a message telling the the Question, Location and Property
        await ctx.send(f':question: The question for {strProperty} at {strPropertyLocation} is: {strQuestion}')

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
        lisCurrentLocation = dbcursor.fetchall()
        tupCurrentLocation = lisCurrentLocation[0]
        strCurrentLocation = tupCurrentLocation[0]

        ## Check if team has said they are going to visit the property ##
        if strCurrentLocation not in self.lisProperties:
            if strCurrentLocation == '':
                await ctx.send(':tophat: You need to use goto first to tell the game where your going! ```&goto brown1```')
                return None
            else:
                await ctx.send(f':tophat: You need to attempt the question at: {strCurrentLocation}, first!')
                return None

        ## Set property to location ##
        strProperty = strCurrentLocation

        ## Get teams money and if they have visited this property from the database ##
        dbcursor.execute(f"SELECT money, {strProperty}_visted FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoneyVisted = dbcursor.fetchall()
        for item in lisMoneyVisted:
            intTeamsMoney = item[0]
            strVisted = item[1]

        ## Check if the team has already visited that property ##
        if strVisted == 'Y':
            await ctx.send(':tophat: You have already answered the question for that property correctly!')
            return None

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
        else:
            blnDoubleRent = False

        ## Check if answer is correct ##
        lisCorrectAnswers = strCorrectAnswers.split('-')
        for item in lisCorrectAnswers:

            # Convert to lowercase and remove spaces #
            strCorrectAnswer = item.lower()
            strCorrectAnswer = re.sub('\s+', '', strCorrectAnswer)

            strAnswer = strAnswer.lower()
            strAnswer = re.sub('\s+', '', strAnswer)
            # Use fuzzy-wuzzy to compare the users answer with the correct answer #
            intPartialRatio = fuzz.partial_ratio(strCorrectAnswer, strAnswer)
            intTokenSetRatio = fuzz.token_set_ratio(strCorrectAnswer, strAnswer)


            if intPartialRatio >= 80 or intTokenSetRatio >= 80:
                blnAnswerCorrect = True
                break
            else:
                blnAnswerCorrect = False

        ## Check if team can afford ##
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

            # Update property visited in database #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visted = 'Y' WHERE id = ?", (strTeamName, ))

            # Update teams money
            intUpdatedMoney = intTeamsMoney + intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))
            await ctx.send(':white_check_mark: This property is also available to buy!')

        ### Answer is correct and property is owned and owner has a group of properties so pay double rent ###
        elif blnAnswerCorrect == True and blnAfford == True and blnDoubleRent == True:

            # Update property visited in database #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visted = 'Y' WHERE id = ?", (strTeamName, ))

            # Update teams money #
            intUpdatedMoney = intTeamsMoney + intValue 
            strValue = str(intValue * 2) #Do I need this line?
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue * 2} on {strProperty}!')
            intUpdatedMoney = intTeamsMoney + (intValue * 2)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))
            await ctx.send(f':white_check_mark: However since: {strOwner} already owns that property and the other properties in the same group you paid: £{strValue} in rent!')

        ### Answer is correct and property is owned so pay rent ###
        elif blnAnswerCorrect == True and blnAfford == True:

            # Update property visited in database #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visted = 'Y' WHERE id = ?", (strTeamName, ))

            # Update teams money #
            intUpdatedMoney = intTeamsMoney + intValue 
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue} on {strProperty}!')
            intUpdatedMoney = intTeamsMoney + intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))
            await ctx.send(f':white_check_mark: However since: {strOwner} already owns that property you paid: £{strValue} in rent!')

        ### Answer is correct however the team can not afford to pay the rent ##
        elif blnAfford == False:
            await ctx.send(':tophat: Answer is correct however you can not afford the rent on that property!')

        ### Answer is incorrect no Double Rent ###
        elif blnAnswerCorrect == False and blnDoubleRent == False:

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue} on {strProperty}, even though they got the answer incorrect!')
            intUpdatedMoney = intTeamsMoney + intValue 
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Notify the user of the highest they were correct #
            if intPartialRatio > intTokenSetRatio:
                await ctx.send(f':negative_squared_cross_mark: Try again! You were {intPartialRatio}% correct!')
            else:
                await ctx.send(f':negative_squared_cross_mark: Try again! You were {intTokenSetRatio}% correct!')

        ### Answer is incorrect and Double Rent ###
        elif blnAnswerCorrect == False and blnDoubleRent == True:

            # Update owners money
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue*2} on {strProperty}, even though they got the answer incorrect!')
            intUpdatedMoney = intTeamsMoney + (intValue * 2)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Notify the user of the highest they were correct #
            if intPartialRatio > intTokenSetRatio:
                await ctx.send(f':negative_squared_cross_mark: Try again! You were {intPartialRatio}% correct!')
            else:
                await ctx.send(f':negative_squared_cross_mark: Try again! You were {intTokenSetRatio}% correct!')

        ### Error ###
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

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def own(self, ctx, strProperty: funToLower):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))

        ## Check if property exits ##
        if strProperty not in self.lisProperties:
            await ctx.send(':tophat: Please enter a valid property! e.g. ```&own brown1``` For a list of properties see the properties channel!')
            return None

        ## Check if a team owns the property ##
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

        ## Check if team can afford ##
        if intTeamsMoney - intValue < 0:
            await ctx.send(':tophat: You can not afford that property!')
            return None

        ## Get and Set Announcement Channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)

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

        ## Get money from database ##
        dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?", (strTeamName ,))
        lisMoney = dbcursor.fetchall()
        tupMoney = lisMoney[0]
        intMoney = tupMoney[0]

        ## Notify the user ##
        await ctx.send(f':dollar: You have £{intMoney}')

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
            await ctx.send(f':house: {strProperty} is not owned by anyone!')
        else:
            tupOwner = lisOwner[0]
            strOwner = tupOwner[0]
            await ctx.send(f':house: {strProperty} is owned by {strOwner}!')

    # Error handling #
    @owner.error
    async def owner_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: {error}``` ')
