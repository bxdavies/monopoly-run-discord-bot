##################
# Import Modules #
##################
import mariadb
from dotenv import load_dotenv
import os
from logging_setup import logger
import sys

##################
# Load .env File #
##################
load_dotenv()

#######################
# Database Connection #
#######################
# Try and Connect to the database if fails exit program #
try:
    dbconnection = mariadb.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        database=os.getenv("DATABASE")
    )
    dbconnection.autocommit = True
    dbconnection.auto_reconnect = True
    dbcursor = dbconnection.cursor()
    
except Exception as e:
    logger.critical(f'CRITICAL Unable to connect to Database: {e}')
    sys.exit(1)
