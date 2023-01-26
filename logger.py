import logging
from logging.config import dictConfig as config


class ColoredFormatter(logging.Formatter):
    base = "%(asctime)s: [%(levelname)s] %(message)s"
    red = "\033[91m"
    yellow = "\033[93m"
    green = "\033[92m"
    white = "\033[0m"
    FORMATS = {
        logging.DEBUG: base,
        logging.INFO: green + base + white,
        logging.WARNING: yellow + base + white,
        logging.ERROR: red + base + white,
    }


LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {'default': {'format': ColoredFormatter.base,
                               'datefmt': '%I:%M:%S %d-%m-%Y'},
                   'colored': {'()': ColoredFormatter}},
    'handlers': {
        'console': {'level': 'INFO',
                    'formatter': 'colored',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout'},
        'file': {
            'level': 'DEBUG',
            'formatter': 'default',
            'class': 'logging.FileHandler',
            'filename': 'bot.log',
            'mode': 'w'
        }
    },
    'loggers': {
        '': {'handlers': ['console', 'file'],
             'level': 'DEBUG',
             'propagate': False},
    }
}
