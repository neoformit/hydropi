"""Manage optional database interface for dynamic app configuration."""

import logging
# import sqlalchemy

logger = logging.getLogger(__name__)


class DB:
    """Database interface for access to dynamic config."""

    def __init__(self):
        """Initiate database connection."""
        self.connected = False
        pass

    def get(self, key):
        """Return value for given field."""
        if self.connected:
            return "the value"

        logger.warning("DB.get(): could not connect to database")
