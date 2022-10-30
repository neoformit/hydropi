"""Test the database interface."""

import os
import sqlite3
import psycopg2
import unittest
from hydropi.config.db import DB


class MockConfig:
    """Mocked config object."""

    DATABASE = {
        'PG_DBNAME': "hydroweb_test",
        'PG_USER': "hydroweb",
        'PG_PASSWORD': "hydroweb",
        'DATALOG_TABLE_NAME': 'datalog',
        'CONFIG_TABLE_NAME': 'config',
        'CONFIG_KEY_FIELD': 'key',
        'CONFIG_VALUE_FIELD': 'value',
        'CONFIG_TYPE_FIELD': 'type',
    }

    KEY_A = 'foo'
    KEY_B = 'bar'
    KEY_INT = 5
    KEY_FLOAT = 0.1
    KEY_BOOL = True


class DatabaseTestCase(unittest.TestCase):
    """Set up and test the database."""

    def setUp(self):
        """Create db context."""
        self.db = DB(MockConfig, assert_schema=False)
        self.tearDown(close=False)

        self.data = {
            'KEY_A': MockConfig.KEY_A,
            'KEY_B': MockConfig.KEY_B,
            'KEY_INT': MockConfig.KEY_INT,
            'KEY_FLOAT': MockConfig.KEY_FLOAT,
            'KEY_BOOL': MockConfig.KEY_BOOL,
        }
        SQL_CREATE_TABLES = (
            f"""CREATE TABLE {self.db.CONFIG_TABLE_NAME}
            ({self.db.CONFIG_KEY_FIELD} text,
             {self.db.CONFIG_VALUE_FIELD} text,
             {self.db.CONFIG_TYPE_FIELD} text)
            """,
            f"CREATE TABLE {self.db.DATALOG_TABLE_NAME} (test_column text)"
        )
        cursor = self.db.connection.cursor()
        for sql in SQL_CREATE_TABLES:
            # Should really check if table exists, then flush if it does or create
            try:
                cursor.execute(sql)
            except sqlite3.OperationalError:
                # sqlite3 sucks at threads, better to use postgres
                pass
        self.db.connection.commit()

    def tearDown(self, close=True):
        """Destroy database context."""
        try:
            print(f"Destroy test table {self.db.CONFIG_TABLE_NAME}")
            self.db.execute(f'DROP TABLE {self.db.CONFIG_TABLE_NAME}')
        except Exception:
            self.db.connection.rollback()
        try:
            print(f"Destroy test table {self.db.DATALOG_TABLE_NAME}")
            self.db.execute(f'DROP TABLE {self.db.DATALOG_TABLE_NAME}')
        except Exception:
            self.db.connection.rollback()
        if close:
            self.db.connection.close()

    def test_can_create_config(self):
        """DB can create config from input."""
        for k, v in self.data.items():
            self.db.set(k, v)
        for k, v in self.data.items():
            self.assertEqual(self.db.get(k), v)

    def test_can_get_config_keys(self):
        """DB can return all config keys."""
        for k, v in self.data.items():
            self.db.set(k, v)
        self.assertEqual(
            self.db.keys(),
            list(self.data.keys())
        )
        self.assertEqual(self.db.get(k), v)

    def test_can_set_config_keys_correctly(self):
        """Ensure that keys are set with the correct type casting."""
        NEW_DATA = {
            'KEY_INT': 2,
            'KEY_FLOAT': 0.15,
            'KEY_BOOL': False,
        }

        # Set default values
        for k, v in self.data.items():
            self.db.set(k, v)

        # Overwrite with new values
        for k, v in NEW_DATA.items():
            self.db.set(k, v)
            self.assertEqual(self.db.get(k), v)
            # Check number of rows - should never be more than one
            rows = self.db.select(
                f'SELECT * FROM {self.db.CONFIG_TABLE_NAME}'
                f" WHERE {self.db.CONFIG_KEY_FIELD}='{k}'"
            )
            self.assertEqual(len(rows), 1)

    def test_can_remove_config_keys(self):
        """DB can delete a config key."""
        for k, v in self.data.items():
            self.db.set(k, v)
        self.db.rm(k)
        self.assertFalse(
            k in self.db.keys()
        )

    def test_will_error_on_config_schema_mismatch(self):
        """DB will alert config table wrong schema."""
        self.db.CONFIG_KEY_FIELD = 'wrong'
        self.assertRaises(ValueError, self.db._assert_schema)
