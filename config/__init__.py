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
import logging

from .db import DB
from .logging import configure as configure_logger

logger = logging.getLogger(__name__)


class Config:
    """Read in, store and update config."""

    def __init__(self, fname):
        """Read in config from yaml."""
        with open(fname) as f:
            __config__ = yaml.safe_load(f)

        for k, v in __config__.items():
            setattr(self, k, v)

        configure_logger(self)

        if hasattr(self, 'DATABASE'):
            self.db = DB()  # NOT YET CONFIGURED
            config.update_from_db()
        else:
            self.db = None

    def update(self, new):
        """Update config from dict.

        Will only create new attributes, only update existing.
        """
        for k, v in new.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def update_from_db(self):
        """Read in config from database connection."""
        if not self.db:
            logger.warning("Trying update config from DB without connection.")
            return
        db_keys = set(self.db.keys).intersection(set(self.__config__))
        db_config = {
            k: self.db.get(k)
            for k in db_keys
        }
        self.update(db_config)

    def parse(self, config):
        """Parse and interpret the config data."""
        if config['CONFIG_DIR'].startswith('~'):
            config['CONFIG_DIR'] = os.path.expanduser(config['CONFIG_DIR'])
        config['TEMP_DIR'] = os.path.join(config['CONFIG_DIR'], 'tmp')
        return config

    def build_dirs(self, dirs):
        """Create missing directories."""
        for d in dirs:
            if not os.path.exists(d):
                os.mkdir(d)


# Load defaults from yaml file
config = Config('config.yml')
