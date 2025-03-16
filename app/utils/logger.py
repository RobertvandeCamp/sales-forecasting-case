from loguru import logger
import sys
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stderr, level="INFO")  # Add stderr handler with INFO level
logger.add("logs/app.log", rotation="10 MB", level="DEBUG")  # Add file handler with DEBUG level

def get_logger():
    """
    Returns a configured logger instance.
    
    Returns:
        logger: Configured logger instance
    """
    return logger 