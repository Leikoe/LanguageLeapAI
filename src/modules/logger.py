from os import getenv
from dotenv import load_dotenv
import logging

load_dotenv()

# logger = logging
# logger.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=getenv('LOG', logging.DEBUG))

logger = logging.getLogger(__name__)
logger.setLevel(getenv('LOG', logging.DEBUG))
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
