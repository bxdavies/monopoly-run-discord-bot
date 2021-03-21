# Monoply-Run-Discord-Bot
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintainability](https://api.codeclimate.com/v1/badges/0b3a1292f8224e543943/maintainability)](https://codeclimate.com/github/bxdavies/Monoply-Run-Discord-Bot/maintainability)
[![CodeFactor](https://www.codefactor.io/repository/github/bxdavies/monoply-run-discord-bot/badge/main)](https://www.codefactor.io/repository/github/bxdavies/monoply-run-discord-bot/overview/main)
[![Updates](https://pyup.io/repos/github/bxdavies/monoply-run-discord-bot/shield.svg)](https://pyup.io/repos/github/bxdavies/monoply-run-discord-bot/)

A game based on the Scout and Girlguide event [Monoply Run](https://monopoly-run.co.uk/). The game works similar to the real world game in which a team visits a property and answers a question at the property. If they are the first one to answer the question correctly they own the property if they are not then they pay rent to the owner.

## Detailed How to ##

## Setup Instructions ##
Setting up Monoply Run Discord is reasonable easy. Monoply Run Discord requires two things Python 3.8 or greater and a MariaDB Server 10.x or MySQL Server

I suggest you use Python 3.9 or greater as it has some performance improvements for C modules.


1. First you need to install a Database do this with: ```sudo apt-get install mariadb-server mariadb-client```

2. Clone the repository with: ```git clone https://github.com/bxdavies/Monoply-Run-Discord-Bot.git```

3. Next you need to create a database and user then create tables with SQL Files... 
    1. ```sudo mysql -u root -p``` (If you have not set a password just press enter when prompted)
    2. Next we create a database: ```CREATE DATABASE monopolyrun;```
    3. Then we create a user: ```CREATE USER 'monopolyrun'@'localhost' IDENTIFIED BY 'YOUR-DB-PASSWORD'; ``` (Change YOUR-DB-PASSWORD to your password)
    4. Grant all privileges to the user on the new database: ```GRANT ALL ON monopolyrun.* TO 'monopolyrun'@'localhost';  ```
    5. Update privileges with: ```FLUSH PRIVILEGES; ```
    6. Exit out: ```Exit```
    7. Go to the SQL folder inside the cloned repository with: ```cd Monoply-Run-Discord-Bot/sql/```
    8. Create the guilds table with: ```sudo mysql -u root -p monopolyrun < tbl_guilds.sql``` (If you have not set a password just press enter when prompted)
    9. Create the questions table with: ```sudo mysql -u root -p monopolyrun < tbl_london.sql```  (If you have not set a password just press enter when prompted)
    10. Secure the MySQL install with: ```sudo mysql_secure_installation``` (Set a root password and then press y for all the questions)

4. Install python and the MariaDB C Connector with: ```sudo apt-get install python3.9 python3.9-dev python3-pip gcc libmariadb3 libmariadb-dev -y```.

5. From the SQL directory go back to the repository folder with ``` cd ..```
6. Install python modules with: ```pip3 install -r requirements.txt ```
7. Create a .env file using the following: ```nano .env``` and then add the following to it: 
```
#Discord Bot Token #
TOKEN=?

# Database Credentials #
HOST="localhost"
PORT=3306
USER="monopolyrun"
PASSWORD="?"
DATABASE="monopolyrun"

# Logging #
LOGGING_LOCATION=/home/ben/
LOG_LEVEL=WARNING
```
Replace the question mark with your token and the other question mark with your database password. (It must have quotes around it!)


You can also set logging location and log level. Its important that the user your running the python script as can write to the log directory. For log level you have a choice of "DEBUG", "INFO", "WARNING", "ERROR" and "CRITICAL".

8. Now start the bot and check for errors with: ```python3 bot.py``` You have now setup Monoply Run Discord if you want to run it as a service see Running the bot as a service: 

### Running the bot as a service ###

## Developer Documentation ##

### File breakdown ###
[logging_setup.py](logging_setup.py) Sets up logging.

[database_connection.py](database_connection.py) Establishes a connection to the database.

[bot.py](bot.py) Is the main starting point for the bot, from here the cogs are loaded.

[game_administration.py](game_administration.py) Is used for administrating the game. This is things such as setting up the game,starting and stop the game and updating the leaderboard and properties channel.

[game_main.py](game_main.py) Is where the actually game play is handled. This includes all the commands players will run to goto and answer questions at properties. 

[game_help.py](game_help.py) Includes the help commands and the help reaction button.

[errors.py](errors.py) Holds all the custom exceptions.

### Formatting ###
Because this a big project the formatting is not necessarily standard but used to show clearly what it does. I have named variables like you would in c# which is not correct for python but I prefer.

#### Variable Names ###
Variable names should start with there type followed by a sensible name. They should be camel case. So for example: ```strTeamName``` is string Team Name.

#### Double Quotes vs Single Quotes #####
Double Quotes are to be used only for SQL quires anything else should be single quotes.

#### Comments ####
The code should be well commented. There is a hierarchy for the comments though. 

A Comment surrounded by comments represents that the code is now doing something completely different to the above.
```
#############
# Info Here #
#############
```
And then any other comments should be standard like so: 
```
# Comment Here #
```

#### Badges ####

[Maintainability](https://codeclimate.com) 

[Code Factor](https://www.codefactor.io)

[Py Up](https://pyup.io)

