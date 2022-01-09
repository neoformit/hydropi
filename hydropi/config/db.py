"""Manage optional database interface for dynamic app configuration."""

import sqlite3
import logging

logger = logging.getLogger(__name__)


class DB:
    """Database interface for access to dynamic config."""

    def __init__(self, config, assert_schema=True):
        """Initiate database connection."""
        try:
            self.connection = sqlite3.connect(config.DATABASE['SQLITE_PATH'])
            self.cursor = self.connection.cursor()
        except Exception as exc:
            logger.error("Could not connect to SQLite database")
            raise exc

        self.DATALOG_TABLE_NAME = config.DATABASE['DATALOG_TABLE_NAME']
        self.CONFIG_TABLE_NAME = config.DATABASE['CONFIG_TABLE_NAME']
        self.CONFIG_KEY_FIELD = config.DATABASE['CONFIG_KEY_FIELD']
        self.CONFIG_VALUE_FIELD = config.DATABASE['CONFIG_VALUE_FIELD']
        if assert_schema:
            self.assert_schema()

    def keys(self):
        """Return list of keys in config table."""
        self.cursor.execute(self.sql_get_config_keys())
        keys = self.cursor.fetchall()
        return [x[0] for x in keys]

    def get(self, key):
        """Return value for given field."""
        self.cursor.execute(self.sql_get_key(key))
        v = self.cursor.fetchall()
        if v:
            return v[0][0]

    def set(self, key, value):
        """Set value for given field."""
        if not self.get(key):
            sql = self.sql_add_key(key, value)
        else:
            sql = self.sql_set_key(key, value)
        self.cursor.execute(sql)
        return self.connection.commit()

    def rm(self, key):
        """Remove a config key from the database."""
        self.cursor.execute(self.sql_rm_key(key))
        self.connection.commit()

    def table_exists(self, name):
        """Return True if table exists in DB."""
        return name in self.sql_get_tables()

    def log_data(self, data):
        """Write current readings to the database."""
        if not self.connection:
            logger.debug("DB.write_row: could not connect to SQLite database")
            return
        self.cursor.execute(self.sql_write_row(data))
        return self.connection.commit()

    def assert_schema(self):
        """Ensure that tables match config."""
        try:
            self.cursor.execute(self.sql_get_table_columns(
                self.CONFIG_TABLE_NAME,
                columns=(self.CONFIG_KEY_FIELD, self.CONFIG_VALUE_FIELD)))
        except Exception:
            raise ValueError(
                "Could not establish config table from database:\n"
                f"CONFIG_VALUE_FIELD: {self.CONFIG_VALUE_FIELD}\n"
                f"CONFIG_KEY_FIELD: {self.CONFIG_KEY_FIELD}\n"
                f"CONFIG_TABLE_NAME: {self.CONFIG_TABLE_NAME}")
        try:
            self.cursor.execute(self.sql_get_table_columns(
                self.DATALOG_TABLE_NAME,
                columns=('id')))
        except Exception:
            raise ValueError(
                "Could not establish datalog table from database:\n"
                f"DATALOG_TABLE_NAME: {self.DATALOG_TABLE_NAME}")

    def sql_add_key(self, key, value):
        """Generate SQL to add a new config key: value pair."""
        if type(value) == str:
            value = f"'{value}'"
        return (
            f"""
            INSERT into {self.CONFIG_TABLE_NAME}
            ('{self.CONFIG_KEY_FIELD}', '{self.CONFIG_VALUE_FIELD}')
            VALUES ('{key}', {value})
            """
        )

    def sql_get_key(self, key):
        """Generate SQL to fetch value for config key."""
        return (
            f"""
            SELECT {self.CONFIG_VALUE_FIELD}
            from {self.CONFIG_TABLE_NAME}
            WHERE {self.CONFIG_KEY_FIELD} = '{key}'
            """
        )

    def sql_set_key(self, key, value):
        """Generate SQL to fetch value for config key."""
        if type(value) == str:
            value = f"'{value}'"
        return (
            f"""
            UPDATE {self.CONFIG_TABLE_NAME}
            SET {self.CONFIG_VALUE_FIELD} = {value}
            WHERE {self.CONFIG_KEY_FIELD} = '{key}'
            """
        )

    def sql_get_config_keys(self):
        """Generate SQL to fetch keys from config table."""
        return (
            f"""
            SELECT {self.CONFIG_KEY_FIELD}
            FROM {self.CONFIG_TABLE_NAME}
            """
        )

    def sql_rm_key(self, key):
        """Remove config key entry."""
        return (
            f"""
            DELETE
            FROM {self.CONFIG_TABLE_NAME}
            WHERE {self.CONFIG_KEY_FIELD} = '{key}'
            """
        )

    def sql_write_datalog_row(self, data):
        """Generate SQL to write row on datalog table."""
        fields = data.items()
        columns = [x[0] for x in fields]
        values = [x[1] for x in fields]

        return (
            f"""
            INSERT INTO {self.DATALOG_TABLE_NAME}
            ({', '.join(columns)})
            VALUES ({', '.join(values)})
            """
        )

    def sql_get_tables(self):
        """Test if table exists."""
        return "SELECT name FROM sqlite_master WHERE type='table'"

    def sql_get_table_columns(self, table, columns=None, limit=10):
        """Return column data from table."""
        if columns:
            return (
                f"""
                SELECT {', '.join(columns)}
                FROM {table}
                LIMIT {limit}
                """
            )
        return (
            f"""
            SELECT *
            FROM {table}
            LIMIT {limit}
            """
        )
