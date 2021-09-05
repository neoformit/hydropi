"""Manage optional database interface for dynamic app configuration."""

import logging

logger = logging.getLogger(__name__)


class DB:
    """Database interface for access to dynamic config."""

    def __init__(self):
        """Initiate database connection."""
        self.connected = False
        self.connect()

    def get(self, key):
        """Return value for given field."""
        if self.connected:
            return "the value"

        logger.warning("DB.get(): could not connect to database")

    def connect():
        """Create connection to the database.

        Do we want to use SQLAlchemy or just SQLite3?
        """
        # config.DATABASE.SQLITE_PATH
        # config.DATABASE.TABLE_NAME
