import logging
import coloredlogs

log_format ="%(asctime)s - %(levelname)s - %(message)s"

def setup_logger(name:str, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    coloredlogs.install(logger=logger, level=level, fmt=log_format)
    return logger

auth_logger = setup_logger("auth")
chat_logger = setup_logger("chatbot")