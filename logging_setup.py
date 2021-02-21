import logging

#################
# Setup Logging #
#################

logging.basicConfig(filename='error.log', 
level=logging.WARNING, 
format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s ", datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger(__name__)