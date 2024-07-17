import logging


def get_logger_relative_path():
    return 'log/main.log'


def config():
    logger = logging.getLogger()
    # Create a logger object
    logger.setLevel(logging.DEBUG)  # Set the overall logging level for the logger

    # Create a console handler and set its level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a file handler and set its level
    file_handler = logging.FileHandler(get_logger_relative_path())
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
