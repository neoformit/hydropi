"""Hardware configuration.

These are default values that may be overwritten at runtime.

- Digital io passes through pins (gpio header pins)
- Analogue io passes through channels (MCP3008 chip interface)

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

    def __init__(self, fname):
        """Read in config from yaml."""
        if not os.path.exists(fname):
            raise FileNotFoundError(
                f'Config file does not exist: {fname}\n\n'
                'Please create a config file for hydropi to set up'
                ' interfaces.\n'
                'For an example see: https://github.com/neoformit/hydropi'
                '/blob/main/config.yml.sample')
        with open(fname) as f:
            for k, v in self.parse(yaml.safe_load(f)).items():
                setattr(self, k, v)

        configure_logger(self)

        if hasattr(self, 'DATABASE'):
            self.db = DB(self)  # NOT YET CONFIGURED
            self.update_from_db()
        else:
            self.db = None

    def parse(self, config):
        """Parse and interpret the config data."""
        if config['CONFIG_DIR'].startswith('~'):
            config['CONFIG_DIR'] = os.path.expanduser(config['CONFIG_DIR'])
        config['TEMP_DIR'] = os.path.join(config['CONFIG_DIR'], 'tmp')
        return config

    def update(self, new):
        """Update config from dict.

        Do not set new attributes, only update existing.
        """
        for k, v in new.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                logger.warning(
                    f"Trying to set unreferenced config attribute {k}")

    def update_from_db(self):
        """Read in config from database connection."""
        if not self.db:
            logger.warning("Trying update config from DB without connection.")
            return
        db_keys = set(self.db.keys).intersection(set(self.__dict__))

        # Request config state from DB
        # This will grab only keys with set values
        db_config = {
            k: self.db[k]
            for k in db_keys
            if self.db.get(k) is not None
        }
        self.update(db_config)


# Load defaults from yaml file
config = Config('config.yml')

# Build dirs
if not os.path.exists(config.CONFIG_DIR):
    os.makedirs(config.CONFIG_DIR)
if os.path.exists(config.TEMP_DIR):
    shutil.rmtree(config.TEMP_DIR)
    os.mkdir(config.TEMP_DIR)
