"""Hardware configuration.

These are default values that may be overwritten at runtime.

- Digital io passes through pins (gpio header pins)
- Analog io passes through channels (MCP3008 chip interface)

Perhaps makes sense to conditionally read/set config from SQLite connection at
runtime, if one exists. Can share a connection with the web app. But need to
access config through an interface `config.get(PARAM)` for this to work
properly.
"""

import os
import yaml
import shutil
import logging

from .db import DB
from .logconf import configure as configure_logger

logger = logging.getLogger(__name__)


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
        configure_logger(self)

        if 'DATABASE' in self.yml:
            self.db = DB(self)
            self.sync_db()

    def __getattr__(self, key):
        """Retrieve config value by key.

        Return attribute preferentially from database, then YAML file.

        WARNING: this can be the source of some freaky bugs!
        """
        if self.db and key in self.db.keys():
            return self.db.get(key)
        if key in self.yml:
            return self.yml[key]

        # Let AttributeError propagate
        super(Config, self).__getattribute__(key)

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
        if not self.db:
            return logger.error("Live config update requires DB connection.")

        db_keys = self.db.keys()

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

# Build dirs
if not os.path.exists(config.CONFIG_DIR):
    os.makedirs(config.CONFIG_DIR)
if os.path.exists(config.TEMP_DIR):
    shutil.rmtree(config.TEMP_DIR)
    os.mkdir(config.TEMP_DIR)
