import logging
from config import LOGGING_LEVEL
# Configure logging
logging.basicConfig(level=LOGGING_LEVEL)

# Get the logger
logger = logging.getLogger(" App Logs ")
