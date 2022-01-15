"""Hardware and parameter configuration.

These are default values that may be overwritten at runtime.

- Digital io passes through PINS (i.e. RPi GPIO header pins)
- Analog signals are read through CHANNELS (MCP3008 chip interface)
- Controllers are actioned through pins, which hit relay channels
- Physical parameters (pressure, pH etc) are also set here. These may be
  exposed for users to manage.

Config is initialized from a config.yml file which must exist in the runtime
directory. Optionally, this file contains a DATABASE section with connection
parameters for a SQLite database. If exists, this connection will be tried
automatically. If successful, config will be written to the DB (if it
doesn't yet exist) and future calls for config attributes will be fetched from
the database. This allows for 'live config', where the application can update
config on-the-fly. Which is great for when users want to modify config through
a web interface.

From here, config.yml is not redundant. It can be used to remove old keys from
the database and set new ones (so that covers key renaming... although the
value will revert to whatever is in config.yml). So though the values may be
different, it should reflect the schema of the database table.
"""

import os
import yaml
import logging

from .db import DB
from .logconf import configure as configure_logger

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
            'help': ('Lower limit of target EC range (μS)'),
        },
        {
            'key': 'EC_MAX',
            'type': 'number',
            'help': ('Upper limit of target EC range (μS)'),
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

DB_CONFIG_KEYS = [
    v['key']
    for v in EXPOSED_CONFIG.values()
]


class Config:
    """Read in, store and update config."""

    db = None

    def __init__(self, fname):
        """Read in config from yaml."""
        if not os.path.exists(fname):
            raise FileNotFoundError(
                f'Config file does not exist: {fname}\n\n'
                'Please create a config file for hydropi to set up'
                ' interfaces.\n'
                'For an example see: https://github.com/neoformit/hydropi'
                '/blob/main/config.yml.sample')

        self.yml = self.parse(fname)
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)
        configure_logger(self)

        if 'DATABASE' in self.yml:
            self.db = DB(self)
            self.sync_db()

    def __getattr__(self, key):
        """Retrieve config value by key.

        Return attribute preferentially from database, then YAML file.
        Only keys that are in DB_CONFIG_KEYS will be fetched from the database.
        """
        if key not in DB_CONFIG_KEYS:
            return self.yml[key]
        if self.db and key in self.db.keys():
            return self.db.get(key)
        if key in self.yml:
            return self.yml[key]

        # Let AttributeError propagate
        self.__getattribute__(key)

    def set(self, key, value):
        """Set config value by key."""
        if self.db:
            self.db.set(key, value)
        else:
            logger.warning("Can't set live config without DB.")

    def parse(self, fname):
        """Parse and interpret the config data.

        This happens before DB connection.
        """
        with open(fname) as f:
            yml = yaml.safe_load(f)
        if yml['CONFIG_DIR'].startswith('~'):
            yml['CONFIG_DIR'] = os.path.expanduser(yml['CONFIG_DIR'])
        yml['TEMP_DIR'] = os.path.join(yml['CONFIG_DIR'], 'tmp')
        return yml

    def update(self, new):
        """Update config from dict."""
        logger.debug(f"Called config.update with data: {new}")
        if not self.db:
            return logger.error("Live config update requires DB connection.")

        db_keys = self.db.keys()
        # logger.debug(f"Database keys exposed for update: {db_keys}")

        for k, v in new.items():
            if k in db_keys:
                self.set(k, v)
            else:
                logger.error(
                    f"Trying to set unreferenced config attribute {k}")

    def sync_db(self):
        """Sync database to match config.yml schema."""
        if not self.db:
            logger.warning("Trying update config from DB without connection.")
            return

        yml_keys = set(self.yml.keys()) - {'DATABASE'}
        db_keys = set(self.db.keys())

        db_absent_keys = yml_keys - db_keys
        db_redundant_keys = db_keys - yml_keys
        for k in db_absent_keys:
            self.set(k, self.yml[k])
        for k in db_redundant_keys:
            self.db.rm(k)


class STATUS:
    """Status display options."""

    NORMAL = 'normal'
    WARNING = 'warning'
    DANGER = 'danger'


# Load defaults from yaml file
config = Config('config.yml')
