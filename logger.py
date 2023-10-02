import logging
import sys


def get_logger(level: str, msg_format: str, filename: str) -> logging.Logger:
    """
    Creates and sets logger for generating log messages in file and console
    outputs.

    :param level: Level of log messages
    :type level: str

    :param msg_format: Format of the log message
    :type msg_format: str

    :param filename: Name of file that will contain log messages
    :type filename: str

    :return: Configured logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    handler = logging.FileHandler(f'{filename}', mode='a')
    formatter = logging.Formatter(msg_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
