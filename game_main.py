##################
# Import Modules #
##################
from discord.ext import commands
from discord import utils, ChannelType
from fuzzywuzzy import fuzz
import re
import asyncio

###########################
# Import External Classes #
###########################
from database_connection import dbcursor
from logging_setup import logging
import errors as MonopolyRunError

##############
# Game Class #
##############
class claGame(commands.Cog):

    ####################
    # Initialize Class #
    ####################
    def __init__(self, bot):
        self.bot = bot
        self.funTeamRole = claGame.funTeamRole

        ## Define some lists to use later ##
        self.lisProperties = ['brown1','brown2','lightblue1','lightblue2','lightblue3','pink1','pink2','pink3','orange1','orange2','orange3','red1','red2','red3','yellow1','yellow2','yellow3','green1','green2','green3','darkblue1','darkblue2']
       

    ##############
    # Converters #
    ##############

    ## Convert to lowercase ##
    def funToLower(strString):
        return strString.lower()

    #############
    # Functions #
    #############

    ## Return users team role ##
    def funTeamRole(ctx):
        lismyRoles = [r.name for r in ctx.author.roles]
        lismyRoles.reverse()
        r = re.compile("team.*")
        if not list(filter(r.match, lismyRoles)):
            raise commands.MissingRole("team?")
        
        return utils.get(ctx.author.roles, name=next(filter(r.match, lismyRoles)))

    ## Return the highest number ##
    def funHighestNumber(intNumber1, intNumber2):
        if intNumber1 > intNumber2:
            return intNumber1
        else:
            return intNumber2

    ##################
    # Command Checks #
    ##################

    ## Check if command is being used in a team channel ##
    def funRoleChannelCheck():
        def predicate(ctx):
            
            ### Check if command is being used in a DM ###
            if ctx.channel.type is ChannelType.private:
                raise commands.NoPrivateMessage
            
            ### Check if the user has a team role ###
            lismyRoles = [r.name for r in ctx.author.roles]
            lismyRoles.reverse()
            r = re.compile("team.*")
            if not list(filter(r.match, lismyRoles)):
                raise commands.MissingRole("team?")
            
            ##  Check if user is using the command in their team channel ##
            if re.search('team', ctx.channel.name) == None:
                raise commands.ChannelNotFound("team?")
            
            x = str(ctx.channel.name)
            y = str(next(filter(r.match, lismyRoles)))
            if x != y:
               raise MonopolyRunError.NotInTeamChannel(next(filter(r.match, lismyRoles)), ctx.channel.name)
            
            return True
        return commands.check(predicate)
            
            
            
    #################
    # Go To Command #
    #################

    @commands.command()
    @funRoleChannelCheck()
    async def goto(self, ctx, strProperty: funToLower):
        
        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(self.funTeamRole(ctx))
        roleTeam = self.funTeamRole(ctx)

        ## Check if property exists ##
        if strProperty not in self.lisProperties:
            raise MonopolyRunError.InvalidPropertyName(strProperty)

        ## Get money and visited from the database ##
        dbcursor.execute(f"SELECT money, {strProperty}_visited FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoneyVisted = dbcursor.fetchall()
        for item in lisMoneyVisted:
            intTeamsMoney = item[0]
            strVisted = item[1]

        ## Check if the team has already visited that property ##
        if strVisted == 'Y':
            raise MonopolyRunError.AlreadyVisted(strProperty)

        ## Get which set of Questions the guild is using ##
        dbcursor.execute("SELECT questions FROM tbl_guilds WHERE id = ?", (strGuildID, ))
        lisQuestions = dbcursor.fetchall()
        tupQuestions = lisQuestions[0]
        strQuestions = tupQuestions[0]

        # Get Location and Question from the Database #
        dbcursor.execute(f"SELECT location, question FROM tbl_{strQuestions} WHERE id = ?" (strProperty, ))
        lisLocationQuestion = dbcursor.fetchall()
        for item in lisLocationQuestion:
            strPropertyLocation = item[0]
            strQuestion = item[1]

        # Update Database to the Location the user is now at
        dbcursor.execute(f"UPDATE tbl_{strGuildID} SET current_location = ? WHERE id = ?", (strProperty, strTeamName))

        # Send user a message telling the the Question, Location and Property
        await ctx.send(f':question: The question for {strProperty} at {strPropertyLocation} is: {strQuestion}')

    ##################
    # Answer Command #
    ##################

    @commands.command(aliases=['answ', 'a'])
    @funRoleChannelCheck()
    async def answer(self, ctx, *, strAnswer):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(self.funTeamRole(ctx))

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
       dbcursor.execute(f"SELECT money, {strProperty}_visited FROM tbl_{strGuildID} WHERE id = ?",  (strTeamName ,))
        lisMoneyVisted = dbcursor.fetchall()
        for item in lisMoneyVisted:
            intTeamsMoney = item[0]
            strVisted = item[1]

        ## Check if the team has already visited that property ##
        if strVisted == 'Y':
            raise MonopolyRunError.AlreadyVisted(strProperty)

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
            dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {lisPropertiesToSelect[0]}_owner = 'Y' and {lisPropertiesToSelect[1]}_owner = 'Y' and {lisPropertiesToSelect[2]}_owner = 'Y'")
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

            print(intTokenSetRatio, intTokenSetRatio)

            if intPartialRatio >= 80 or intTokenSetRatio >= 80:
                blnAnswerCorrect = True
                break
            else:
                blnAnswerCorrect = False

    
        ## Checks ##
        ### Answer is correct AND the property is NOT owned ### YES
        if blnAnswerCorrect == True and strOwner == None and blnDoubleRent == False: 

            # Update property visited in database #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visited = 'Y' WHERE id = ?", (strTeamName, ))

            # Update teams money and set owner #
            intUpdatedMoney = intTeamsMoney + intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = '{intUpdatedMoney}', {strProperty}_owner = 'Y' WHERE id = '{strTeamName}'")

            # Notify announcements of the Owner #
            catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
            chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)
            await chaAnnouncementChannel.send(f':house: {strTeamName} now owns {strProperty}!')

            await ctx.send(f':white_check_mark: You now own {strProperty}!')

        ### Answer is correct AND the property is owned AND the team can afford rent ### YES
        elif blnAnswerCorrect == True and strOwner != None and blnDoubleRent == False: 

            # Update property visited in database #
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visited = 'Y' WHERE id = ?", (strTeamName, ))

            # Update teams money #
            intUpdatedMoney = intTeamsMoney + intValue 
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue} on {strProperty}!')
            intUpdatedMoney = intTeamsMoney + intValue
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))
            await ctx.send(f':white_check_mark: However since: {strOwner} already owns that property you paid: £{intValue} in rent!')

        ### Answer is correct AND the property is owned  AND double rent AND the team can afford rent ### YES
        elif blnAnswerCorrect == True and strOwner != None and blnDoubleRent == True:

            # Update property visited in database #
              dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_visited = 'Y' WHERE id = ?", (strTeamName, ))

            # Update teams money #
            intUpdatedMoney = intTeamsMoney + intValue 
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strTeamName))

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue * 2} on {strProperty}!')
            intUpdatedMoney = intTeamsMoney + (intValue * 2)
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))
            await ctx.send(f':white_check_mark: However since: {strOwner} already owns that property and the other properties in the same group you paid: £{intValue*2} in rent!')

        ### Answer is incorrect AND the property is NOT owned ###
        elif blnAnswerCorrect == False and strOwner == None and blnDoubleRent == False:
            await ctx.send(f':negative_squared_cross_mark: Try again! You were {claGame.funHighestNumber(intPartialRatio, intTokenSetRatio)}% correct!')

        ### Answer is incorrect AND the property is owned AND the team can afford rent ### YES
        elif blnAnswerCorrect == False and strOwner != None and blnDoubleRent == False:

            await ctx.send(f':negative_squared_cross_mark: Try again! You were {claGame.funHighestNumber(intPartialRatio, intTokenSetRatio)}% correct! However since: {strOwner} already owns that property you paid: £{intValue} in rent!')

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue} on {strProperty}, even though they got the answer incorrect!')
            intUpdatedMoney = intTeamsMoney + intValue 
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))

        ### Answer is incorrect AND the property is owned AND double rent AND the team can afford rent ### YES
        elif blnAnswerCorrect == False and strOwner != None and blnDoubleRent == True:

            await ctx.send(f':negative_squared_cross_mark: Try again! You were {claGame.funHighestNumber(intPartialRatio, intTokenSetRatio)}% correct! However since: {strOwner} already owns that property and the other properties in the same group you paid: £{intValue*2} in rent!')

            # Update owners money #
            chaOwner = utils.get(ctx.guild.channels, name=strOwner)
            await chaOwner.send(f':dollar: {strTeamName} just paid £{intValue} on {strProperty}, even though they got the answer incorrect!')
            intUpdatedMoney = intTeamsMoney + (intValue * 2) 
            dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strOwner))


        ### Error ###
        else:
            logging.error(f'Unexpected error: Answer, Correct Answer, Answer Correct, Owner, Double Rent, Afford is not valid! {strAnswer, strCorrectAnswer, blnAnswerCorrect, strOwner, blnDoubleRent, }')
            await ctx.send(f':satellite: An unexpected error occurred! ```The error is: Answer, Correct Answer, Answer Correct, Owner, Double Rent, Afford is not valid! {strAnswer, strCorrectAnswer, blnAnswerCorrect, strOwner, blnDoubleRent, }``` ')


    #################
    # Money Command #
    #################

    @commands.command()
    @funRoleChannelCheck()
    async def money(self, ctx):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(self.funTeamRole(ctx))

        ## Get money from database ##
        dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?", (strTeamName ,))
        lisMoney = dbcursor.fetchall()
        tupMoney = lisMoney[0]
        intMoney = tupMoney[0]

        ## Notify the user ##
        await ctx.send(f':dollar: You have £{intMoney}')

    ##########################
    # Property Owner Command #
    ##########################

    @commands.command()
    @funRoleChannelCheck()
    async def owner(self, ctx, strProperty: funToLower):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)

        ## Check if property exists ##
        if strProperty not in self.lisProperties:
            raise MonopolyRunError.InvalidPropertyName(strProperty)


        ## Check if a team owns the property ##
        dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {strProperty}_owner = 'Y'")
        lisOwner = dbcursor.fetchall()
        if not lisOwner:
            await ctx.send(f':house: {strProperty} is not owned by anyone!')
        else:
            tupOwner = lisOwner[0]
            strOwner = tupOwner[0]
            await ctx.send(f':house: {strProperty} is owned by {strOwner}!')

    ##################
    # Error Handling #
    ##################
    async def cog_command_error(self, ctx, error):
        
        #  Missing Role #
        if isinstance(error, commands.MissingRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')

        # Channel Not Found #
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')

        # Missing Required Argument #
        elif isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.name == 'goto' or ctx.command.name == 'owner':
                await ctx.send(f':no_entry: You need to specify the property! e.g. ```mr {ctx.command.name} brown1```')
            elif ctx.command.name == 'answer':
                await ctx.send(f':no_entry: You need to specify the answer! e.g. ```mr {ctx.command.name} hello world```')
            else:
                await ctx.send(f':no_entry: That command is missing a required argument!')

        # No Private Message #
        elif isinstance(error,commands.NoPrivateMessage):
            await ctx.author.send(':no_entry: Please use all commands in a Server (Not Direct Messages)!')

        # Invalid Property Name #
        elif isinstance(error, MonopolyRunError.InvalidPropertyName):
            await ctx.send(f':no_entry: Please enter a valid property! e.g. ```mr {ctx.command.name} brown1``` For a list of properties see the properties channel!')
        
        # Already visited #
        elif isinstance(error,MonopolyRunError.AlreadyVisted):
            await ctx.send(':no_entry: You have already answered the question for that property correctly!')

        # Any other error #
        else:
            logging.error(f'Unexpected error: {error}')
            await ctx.send(f':satellite: (Main)An unexpected error occurred! ```The error is: {error}``` ')