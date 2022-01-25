"""Logging configuration."""

import os
import logging
import logging.config


def configure(config):
    """Configure app logger."""
    if os.environ.get('DISABLE_HYDROPI_LOG'):
        logger = logging.getLogger('hydropi')
        logger.info("Skip Hydropi log config (DISABLE_HYDROPI_LOG = True)")
        return

    console_log_level = 'DEBUG' if config.DEBUG else 'INFO'

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(levelname).4s | %(asctime)s | %(module)-12s| %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'style': "%",
            },
        },
        'handlers': {
            'file': {
                'delay': True,
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1000000,  # 1MB ~ 20k rows
                'backupCount': 5,
                'filename': os.path.join(config.CONFIG_DIR, 'hydro.log'),
                'mode': 'a',
                'formatter': 'standard',
            },
            'debug_file': {
                'delay': True,
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1000000,  # 1MB ~ 20k rows
                'backupCount': 5,
                'filename': os.path.join(config.CONFIG_DIR, 'hydro.debug.log'),
                'mode': 'a',
                'formatter': 'standard',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': console_log_level,
                'formatter': 'standard',
            },
        },
        'loggers': {
            'hydropi': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': True,
            },
        }
    })
