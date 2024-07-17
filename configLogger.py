import logging


def get_logger_relative_path():
    return 'log/persistent.log'


def get_logger_overwrite_path():
    return 'log/per_run.log'


def config():
    logger = logging.getLogger()
    # Create a logger object
    logger.setLevel(logging.INFO)  # Set the overall logging level for the logger

    # Create a console handler and set its level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a file handler that appends to older logs and set its level
    file_handler_append = logging.FileHandler(get_logger_relative_path(), mode='a')
    file_handler_append.setLevel(logging.INFO)

    # Create a file handler that overwrites older logs and set its level
    file_handler_overwrite = logging.FileHandler(get_logger_overwrite_path(), mode='w')
    file_handler_overwrite.setLevel(logging.INFO)

    # Create a formatter and set it for all handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    file_handler_append.setFormatter(formatter)
    file_handler_overwrite.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler_append)
    logger.addHandler(file_handler_overwrite)
