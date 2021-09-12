"""Manage optional database interface for dynamic app configuration."""

import sqlite3
import logging

logger = logging.getLogger(__name__)


class DB:
    """Database interface for access to dynamic config."""

    def __init__(self, config):
        """Initiate database connection."""
        try:
            self.connection = sqlite3.connect(config.DATABASE.SQLITE_PATH)
        except Exception:
            logger.warning("Could not connect to SQLite database")
            return
        # Assert tables have correct column names

    def get(self, key):
        """Return value for given field."""
        if not self.connection:
            logger.debug("DB.get: could not connect to SQLite database")
            return
        c = self.connection.cursor()
        return c.execute(sql_get_key(key))

    def write_stat(self, data):
        """Write current readings to the database."""
        if not self.connection:
            logger.debug("DB.write_row: could not connect to SQLite database")
            return
        c = self.connection.cursor()
        return c.execute(sql_write_row(data))


def sql_get_key(key):
    """Generate SQL to fetch value for config key."""
    return (
        f"SELECT {config.DATABASE.CONFIG_VALUE_FIELD}"
        f" from {config.DATABASE.CONFIG_TABLE_NAME}"
        f" WHERE {config.DATABASE.CONFIG_KEY_FIELD} = '{key}';"
    )


def sql_write_row(data):
    """Generate SQL to write row to read data table."""
    fields = data.items()
    columns = [x[0] for x in fields]
    values = [x[1] for x in fields]

    return (
        f"INSERT INTO {config.DATABASE.READINGS_TABLE_NAME}"
        f" ({', '.join(columns)})"
        f" VALUES ({', '.join(values)});"
    )
