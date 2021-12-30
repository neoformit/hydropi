"""Logging configuration."""

import os
import logging
import logging.config

logger = logging.getLogger(__name__)


def configure(config):
    """Configure app logger."""
    log_level = 'DEBUG' if config.DEBUG else 'INFO'
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(levelname)5s | %(asctime)s | %(module)12s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'style': "%",
            },
        },
        'handlers': {
            'file': {
                'delay': True,
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1000000,  # 1MB ~ 20k rows
                'backupCount': 5,
                'filename': os.path.join(config.CONFIG_DIR, 'hydro.log'),
                'mode': 'a',
                'formatter': 'standard',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
            },
        },
        'root': {
            'level': log_level,
            'handlers': ['console', 'file'],
        },
    })
