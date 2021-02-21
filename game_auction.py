##################
# Import Modules #
##################
from discord.ext import commands, tasks
from discord import utils
from database_connection import dbcursor
from logging_setup import logging
import datetime

#################
# Auction Class #
#################
class claAuction (commands.Cog):

    ####################
    # Initialize Class #
    ####################
    def __init__(self, bot):
        self.bot = bot

        ## Define some lists to use later ##
        self.lisTeamChannels = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']
        self.lisTeamRoles = ['team1', 'team2', 'team3', 'team4', 'team5', 'team6', 'team7', 'team8', 'team9']
        self.lisProperties = ['brown1','brown2','lightblue1','lightblue2','lightblue3','pink1','pink2','pink3','orange1','orange2','orange3','red1','red2','red3','yellow1','yellow2','yellow3','green1','green2','green3','darkblue1','darkblue2']
        self.AcutionLoop = claAuction.AcutionLoop

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

    ## Check if command is being used in the auction channel ##
    def funAuctionChannel(ctx):
        if ctx.channel.name == "auction":
            return True
        else:
            return False

    ##########################
    # I want to Sell Command #
    ##########################

    # Command Handling #
    @commands.command()
    @commands.check(funValidChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def iwts(self, ctx, strProperty: funToLower, intStartingPrice: int):

        ## Declare some key variables ##
        strGuildID = str(ctx.guild.id)
        strTeamName = str(utils.find(lambda i: i.name in self.lisTeamRoles, ctx.author.roles))

        ## Check if Price is Valid ##
        if intStartingPrice < 1 or intStartingPrice > 10000:
            await ctx.send(':tophat: Please enter a valid price between £1 and £10000!')
            return None

        ## Check if property exists ##
        if strProperty not in self.lisProperties:
            await ctx.send(':tophat: Please enter a valid property! e.g. ```&iwts brown1 100``` For a list of properties see the properties channel!')
            return None

        ## Check if an auction is already in progress ##
        dbcursor.execute("SELECT guild FROM tbl_auctions WHERE guild = ?", (strGuildID, )) 
        lisGuild = dbcursor.fetchall()
        if lisGuild:
            await ctx.send(':tophat: An auction is already in progress!')
            return None

        ## Check if player owns that property ##
        dbcursor.execute(f"SELECT {strProperty}_owner FROM tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisOwner = dbcursor.fetchall()
        tupOwner = lisOwner[0]
        strOwner = tupOwner[0]
        if strOwner != "Y":
            await ctx.send(':tophat: You do not own that property so can not sell it!') 
            return None

        ## Calculate end time ##
        dtAuctionStartTime = datetime.datetime.now()
        dtAuctionEndTime = dtAuctionStartTime + datetime.timedelta(minutes=1) 

        ## Create record in database ##
        dbcursor.execute("INSERT INTO tbl_auctions (guild, property, bid, end_time) VALUES (?, ?, ?, ?)", (strGuildID, strProperty, intStartingPrice, dtAuctionEndTime))

        ## Get and Set Announcement &  Auction Channel ##
        catMonopolyRun = utils.get(ctx.guild.categories, name="Monopoly Run")
        chaAnnouncementChannel = utils.get(ctx.guild.channels, name="announcements", category_id=catMonopolyRun.id)
        chaAuctionChannel = utils.get(ctx.guild.channels, name="auction", category_id=catMonopolyRun.id)

        ## Send Messages ##
        await chaAnnouncementChannel.send(f':dollar: Auction for: {strProperty} with a starting price of £{intStartingPrice} starting in #auction NOW!')
        await chaAuctionChannel.send(f'Auction for: {strProperty} with a starting price of £{intStartingPrice} Lasting for 2 minutes')

        ## Start 2 minute loop ##
        
        self.AcutionLoop.start(ctx, strProperty, dtAuctionEndTime, strGuildID, chaAuctionChannel)

    # Error Handling #
    @iwts.error
    async def iwts_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in you team channel e.g. team1!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':no_entry: Please enter both property and starting price!  ```e.g. &iwts brown1 100```')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(':no_entry: Please enter a valid starting price!')
        else:
            await ctx.send(f':satellite: An unexpected error occurred! The error is: ```{error}``` ')
    
    ###############
    # Bid command #
    ###############

    # Command Handling
    @commands.command()
    @commands.check(funAuctionChannel)
    @commands.has_any_role("team1", "team2", "team3", "team4", "team5", "team6", "team7", "team8", "team9")
    async def bid(self, ctx, intBidAmount: int):
        
        # Define some key variables 
        strTeamName = str(ctx.author.roles[1])
        strGuildID = str(ctx.guild.id)

        # Check if price is Valid
        if intBidAmount < 1 or intBidAmount > 10000:
            await ctx.send(':tophat: Please enter a valid price between £1 and £1000!')
            return None

        # Get property, bid and end time from the database
        dbcursor.execute("SELECT property, bid, end_time FROM tbl_auctions WHERE guild = ?", (strGuildID, ))
        lisAuctionInfo = dbcursor.fetchall()

        # Check if Auction is in Progress
        if not lisAuctionInfo:
            await ctx.send(':tophat: Action has either finished or is not running!')
            return None

        # Set variables 
        for item in lisAuctionInfo:
            strPropertyinAuction = item[0]
            intHighestBid = int(item[1])
            dtAuctionEndTime = item[2]

        # Check if team has the answer right
        dbcursor.execute(f"SELECT {strPropertyinAuction}_visted FROM tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisAnswered = dbcursor.fetchall()
        tupAnswered = lisAnswered[0]
        strAnswered = str(tupAnswered[0])
        if strAnswered != 'Y':
            await ctx.send(':tophat: You have not answered the question correctly!')
            return None

        # Check if team can Afford
        dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?", (strTeamName, ))
        lisMoney = dbcursor.fetchall()
        tupMoney = lisMoney[0]
        intMoney = int(tupMoney[0])
        
        if intMoney < intBidAmount:
            await ctx.send(':tophat: You can not afford to bid that much!')
            return None
        
        # Check if Bid is greater than the Highest Bidder
        if intBidAmount < intHighestBid:
            await ctx.send(':tophat: You must bid higher than highest bid or starting price!')
            return None

        # Assuming everything is correct so updating variables
        dbcursor.execute("UPDATE tbl_auctions SET bidder = ?, bid = ?  WHERE guild = ?", (strTeamName, intBidAmount, strGuildID))
        await ctx.send(f':dollar: Current Bid is: £{intBidAmount} From: {strTeamName}')

    # Error Handling
    @bid.error
    async def bid_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send(':no_entry: You must have a team role! For example role: team1')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(':no_entry: You must use this command in the auction channel!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':no_entry: Please enter bid amount!  ```e.g. &bid 100```')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(':no_entry: Please enter a valid bid amount!')
        else:
            await ctx.send(f':satellite: An unexpected error occurred! The error is: ```{error}``` ')
    
    ################
    # Auction Loop #
    ################
    @tasks.loop(seconds=1.0, count=70)
    async def AcutionLoop(ctx, strProperty, dtAuctionEndTime, strGuildID, chaAuctionChannel):
        if datetime.datetime.now().strftime('%H:%M:%S') == dtAuctionEndTime.strftime('%H:%M:%S'):

            dbcursor.execute("SELECT bidder, bid  FROM tbl_auctions WHERE guild = ?", (strGuildID, ))
            lisBidderBid = dbcursor.fetchall()
            for item in lisBidderBid:
                strBidder = item[0]
                intBidAmount = int(item[1])
            # Update Money Code
            if strBidder == None:
                await chaAuctionChannel.send(f'Auction has finished with no sale!')
            elif strBidder != None:
                # Get current owner
                dbcursor.execute(f"SELECT id FROM tbl_{strGuildID} WHERE {strProperty}_owner = 'y'")
                lisOwner = dbcursor.fetchall()
                tupOwner = lisOwner[0]
                strOwner = tupOwner[0]

                # Remove owner 
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_owner = 'N' WHERE id = ?", (strOwner, ))
                
                # Set owner to auction winner
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET {strProperty}_owner = 'Y' WHERE id = ?", (strBidder, ))
                
                # Take bid away from teams money
                dbcursor.execute(f"SELECT money FROM tbl_{strGuildID} WHERE id = ?", (strBidder, ))
                lisMoney = dbcursor.fetchall()
                tupMoney = lisMoney[0]
                intMoney = int(tupMoney[0])
                intUpdatedMoney = intMoney - intBidAmount
                
                dbcursor.execute(f"UPDATE tbl_{strGuildID} SET money = ? WHERE id = ?", (intUpdatedMoney, strBidder))
                
                # Let users know result
                await chaAuctionChannel.send(f':dollar: Auction has finished so: {strProperty} is sold to: {strBidder}')
            else:
                print("ERORR")
            # Delete record from auction table
            dbcursor.execute("DELETE FROM tbl_auctions WHERE guild = ?", (strGuildID, ))
            claAuction.AcutionLoop.stop()