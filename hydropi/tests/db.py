"""Test the database interface."""

import os
import sqlite3
import unittest
from hydropi.config.db import DB


class MockConfig:
    """Mocked config object."""

    DATABASE = {
        'SQLITE_PATH': 'test.db.sqlite3',
        'DATALOG_TABLE_NAME': 'datalog',
        'CONFIG_TABLE_NAME': 'config',
        'CONFIG_KEY_FIELD': 'key',
        'CONFIG_VALUE_FIELD': 'value',
    }

    KEY_A = 'foo'
    KEY_B = 'bar'


class DatabaseTestCase(unittest.TestCase):
    """Set up and test the database."""

    def setUp(self):
        """Create db context."""
        self.db = DB(MockConfig, assert_schema=False)
        self.data = {
            'KEY_A': MockConfig.KEY_A,
            'KEY_B': MockConfig.KEY_B,
        }
        SQL_CREATE_TABLES = (
            f"""CREATE TABLE {self.db.CONFIG_TABLE_NAME}
            ({self.db.CONFIG_KEY_FIELD} text,
             {self.db.CONFIG_VALUE_FIELD} text)
            """,
            f"CREATE TABLE {self.db.DATALOG_TABLE_NAME} (test_column text)"
        )
        for sql in SQL_CREATE_TABLES:
            try:
                self.db.cursor.execute(sql)
            except sqlite3.OperationalError:
                pass
        self.db.connection.commit()

    def tearDown(self):
        """Destroy database context."""
        self.db.connection.close()
        os.remove(MockConfig.DATABASE['SQLITE_PATH'])

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
        self.assertRaises(ValueError, self.db.assert_schema)
