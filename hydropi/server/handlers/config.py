"""Handlers for interacting with hydropi config."""

import logging
from hydropi.config import config, EXPOSED_CONFIG

logger = logging.getLogger('hydropi')


def get(name=None):
    """Return config grouped by controller."""
    data = {
        g: [
            {
                **param,
                'value': getattr(config, param['key']),
            } for param in params
        ] for g, params in EXPOSED_CONFIG.items()
    }
    if name:
        return data[name]
    return data


def set(data):
    """Update config with given data."""
    logger.debug(f"Request received: config.set | DATA: {data}")
    config.update(data)
