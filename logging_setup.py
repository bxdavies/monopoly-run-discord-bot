##################
# Import Modules #
##################
import logging
from dotenv import load_dotenv
import os
import getpass
import sys

##################
# Load .env File #
##################
load_dotenv()

############################
# Create Logging Directory #
############################
strLoggingLocation = os.getenv("LOGGING_LOCATION")

## Default to working directory if strLoggingLocation is empty ##
if not strLoggingLocation:
    print('WARN Logging to application directory as LOGGING_LOCATION is not specified!')
    strLoggingLocation = os.getcwd() + '/Monopoly-Run-bot.log'
else:
    ### Check Directory exits ###
    if os.path.isdir(strLoggingLocation) == True:
        strLoggingLocation = strLoggingLocation + 'Monopoly-Run-bot.log'

    ### Create Directory is not exits ###
    else:
        try:
            os.mkdir(strLoggingLocation)
            strLoggingLocation = strLoggingLocation + 'Monopoly-Run-bot.log'
        except PermissionError:
            print(f'CRITICAL Please check {getpass.getuser()} has read/write access to {strLoggingLocation}')
            sys.exit(1)
        except Exception as e:
            print(f'CRITICAL Unknown error when setting up Logging: {e}')
            sys.exit(1)

#################
# Setup Logging #
#################
try:
    logging.basicConfig(filename=strLoggingLocation,
    level = getattr(logging, os.getenv('LOG_LEVEL').upper()),
    format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s ", datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger(__name__)
    logging.info('Log File Created')

except PermissionError:
    print(f'CRITICAL Please check {getpass.getuser()} has read/write access to {strLoggingLocation}')
    sys.exit(1)
    
except Exception as e:
    print(f'CRITICAL Unknown error when setting up Logging: {e}')
    sys.exit(1)

