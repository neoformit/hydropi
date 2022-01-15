"""Handlers for interacting with hydropi config."""

import logging
from pprint import pformat
from hydropi.config import config
from hydropi import interfaces

logger = logging.getLogger('hydropi')

EXPOSED_CONFIG = {
    'general': (
        {
            'key': 'QUIET_TIME_START',
            'type': 'text',
            'help': 'Time of evening when pump should no longer run (HH:MM)',
        },
        {
            'key': 'QUIET_TIME_END',
            'type': 'text',
            'help': 'Time of morning when pump can resume operation (HH:MM)',
        },
        {
            'key': 'SWEEP_CYCLE_MINUTES',
            'type': 'number',
            'help': 'Interval between status check and balance (minutes)',
        },
    ),
    'ec': (
        {
            'key': 'EC_MIN',
            'type': 'number',
            'help': ('Lower limit of target EC range'
                     f' ({interfaces.ECSensor.UNIT})'),
        },
        {
            'key': 'EC_MAX',
            'type': 'number',
            'help': ('Upper limit of target EC range'
                     f' ({interfaces.ECSensor.UNIT})'),
        },
        {
            'key': 'EC_ADDITION_ML',
            'type': 'number',
            'help': ('Volume of nutrient to deliver before mix and re-check'
                     ' (ml)'),
        },
    ),
    'ph': (
        {
            'key': 'PH_MIN',
            'type': 'number',
            'help': 'Lower limit of target pH range',
        },
        {
            'key': 'PH_MAX',
            'type': 'number',
            'help': 'Upper limit of target pH range',
        },
        {
            'key': 'PH_ADDITION_ML',
            'type': 'number',
            'help': ('Volume of pH-down to deliver before mix and re-check'
                     ' (ml)'),
        },
    ),
    'mist': (
        {
            'key': 'MIST_CYCLE_MINUTES',
            'type': 'number',
            'help': 'Interval between mist release (minutes)',
        },
        {
            'key': 'MIST_CYCLE_NIGHT_MINUTES',
            'type': 'number',
            'help': 'Interval while misting during quiet time (minutes)',
        },
        {
            'key': 'MIST_DURATION_SECONDS',
            'type': 'number',
            'help': 'Duration of each mist release (seconds)',
        },
    ),
    'mix': (
        {
            'key': 'MIX_PUMP_SECONDS',
            'type': 'number',
            'help': ('Duration of mixing after a nutrient tank addition'
                     ' (seconds)'),
        },
        {
            'key': 'MIX_ADDITION_DELAY_SECONDS',
            'type': 'number',
            'help': 'Duration of mixing before an addition is made (seconds)',
        },
    ),
    'depth': (
        {
            'key': 'VOLUME_TARGET_L',
            'type': 'number',
            'help': 'Target volume for the nutrient tank (litres)',
        },
        {
            'key': 'VOLUME_TOLERANCE',
            'type': 'number',
            'help': 'Accepted deviation from target volume (proportion)',
        },
        {
            'key': 'WATER_ADDITION_SECONDS',
            'type': 'number',
            'help': ('Duration of water addition before re-measurement of tank'
                     ' depth (seconds)'),
        },
        {
            'key': 'WATER_MAX_ADDITION_SECONDS',
            'type': 'number',
            'help': ('Maximum duration of water delivery in one sweep event'
                     ' - this is a failsafe against accidental flooding'
                     ' (seconds)'),
            },
    ),
    'pressure': (
        {
            'key': 'MIN_PRESSURE_PSI',
            'type': 'number',
            'help': 'Threshold tank pressure to trigger a refill (PSI)',
        },
        {
            'key': 'MAX_PRESSURE_PSI',
            'type': 'number',
            'help': 'Tank pressure where refill will terminate (PSI)',
        },
    ),
}


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
    logger.debug("hydropi.handlers.config.get() data:")
    logger.debug(pformat(data))
    if name:
        return data[name]
    return data


def set(data):
    """Update config with given data."""
    logger.debug(f"Request received: config.set | DATA: {data}")
    config.update(data)
