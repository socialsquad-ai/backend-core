import sys

from loguru import logger

from utils.contextvar import get_request_metadata

# Configure logger with a default sink to stdout
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)


class LoggerUtil:
    @classmethod
    def create_info_log(cls, message):
        # Truncate message if too long
        message = message[:5000]
        metadata = get_request_metadata()
        # Combine message with metadata
        logger.bind(**metadata).info(message)

    @classmethod
    def create_error_log(cls, message):
        # Truncate message if too long
        message = message[:5000]
        metadata = get_request_metadata()
        # Combine message with metadata
        logger.bind(**metadata).error(message)
