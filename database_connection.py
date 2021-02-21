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
try:
    dbconnection = mariadb.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        database=os.getenv("DATABASE")
    )
    dbconnection.autocommit = True
    dbcursor = dbconnection.cursor()
except mariadb.Error as e:
    logger.critical(f'Unable to connect to Database: {e}')
    sys.exit(1)