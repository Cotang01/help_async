import logging
import sys


def log(log_config, json_data):
    """
    Creates and sets logger for generating logs in .log file and console
    outputs.

    :param log_config: Logger configuration
    :type log_config: str

    :param json_data: JSON data for logger configuration
    :type json_data: dict

    :return: Configured logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(json_data['level'])
    handler = logging.FileHandler(f'{json_data["filename"]}', mode='a')
    formatter = logging.Formatter(json_data['format'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.info(log_config)
    return logger
