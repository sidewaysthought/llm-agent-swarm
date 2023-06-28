import logging
import datetime
import argparse

class LoggerConfig:

    def __init__(self, debug_enabled = False):
        self.debug_enabled = debug_enabled
        self.log_count = 1

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if self.debug_enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        info_formatter = logging.Formatter('%(asctime)s\t%(eventtype)s\t%(issuer)s\t%(message)s')
        conv_formatter = logging.Formatter('%(asctime)s\t%(id)s\t%(from)s\t%(to)s\t%(message)s')

        info_handler = logging.FileHandler(f'info_{current_date}_{self.log_count}.log')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(info_formatter)

        error_handler = logging.FileHandler(f'error_{current_date}_{self.log_count}.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(info_formatter)

        debug_handler = logging.FileHandler(f'debug_{current_date}_{self.log_count}.log')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(info_formatter)

        conv_handler = logging.FileHandler(f'conversations_{current_date}_{self.log_count}.log')
        conv_handler.setLevel(logging.INFO)
        conv_handler.setFormatter(conv_formatter)

        logger.addHandler(info_handler)
        logger.addHandler(error_handler)
        logger.addHandler(debug_handler)
        logger.addHandler(conv_handler)

        return logger
