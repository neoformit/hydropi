"""Logging configuration."""

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
                'format': '{levelname} | {asctime} | {module}: {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'delay': True,
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'maxBytes': 1000000,  # 1MB ~ 20k rows
                'backupCount': 5,
                'filename': 'hydro.log',
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
