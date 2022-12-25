"""Manage optional database interface for dynamic app configuration."""

import logging
import psycopg2
from datetime import datetime

logger = logging.getLogger('hydropi')

TYPECAST = {
    'int': int,
    'str': str,
    'bool': lambda x: bool(int(x)),
    'float': float,
}


class SchemaError(ValueError):
    """An exception with the database schema."""

    pass


class DB:
    """Database interface for access to dynamic config."""

    def __init__(self, config, assert_schema=True):
        """Initiate database connection."""
        self.connection = psycopg2.connect(
            dbname=config.DATABASE['PG_DBNAME'],
            user=config.DATABASE['PG_USER'],
            password=config.DATABASE['PG_PASSWORD'],
            host='127.0.0.1',
        )
        self.DATALOG_TABLE_NAME = config.DATABASE['DATALOG_TABLE_NAME']
        self.CONFIG_TABLE_NAME = config.DATABASE['CONFIG_TABLE_NAME']
        self.CONFIG_KEY_FIELD = config.DATABASE['CONFIG_KEY_FIELD']
        self.CONFIG_VALUE_FIELD = config.DATABASE['CONFIG_VALUE_FIELD']
        self.CONFIG_TYPE_FIELD = config.DATABASE['CONFIG_TYPE_FIELD']
        self.config = config
        if assert_schema:
            self._assert_schema()

    # SQL Execution
    # -------------------------------------------------------------------------

    def execute(self, sql):
        """Execute SQL and log SQL statement if error."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
        except Exception as exc:
            logger.error(f'SQL: {sql}')
            raise exc
        finally:
            cursor.close()

    def select(self, sql):
        """Perform a SQL select and return the data."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
        except Exception as exc:
            logger.error(f'SQL: {sql}')
            raise exc
        finally:
            cursor.close()

        return data

    # Queries
    # -------------------------------------------------------------------------

    def keys(self):
        """Return list of keys in config table."""
        keys = self.select(self.sql_get_config_keys())
        return [x[0] for x in keys]

    def get(self, key):
        """Return value for given field."""
        r = self.select(self.sql_get_key(key))
        if r:
            v, type_str = r[0]
            return TYPECAST[type_str](v)

    def set(self, key, value):
        """Set config value for given field."""
        if value == '' or value is None:
            raise ValueError(
                f"config.set received empty config value: {value}")
        if self.get(key) is None:
            sql = self.sql_add_key(key, value)
            logger.info("SQL ADD KEY:\n" + sql)
        else:
            # Assert that value can be cast to field type
            type_str = self.select(self.sql_get_key(key))[0][1]
            try:
                TYPECAST[type_str](value)
            except ValueError as exc:
                logger.error(
                    'Failed to cast type while setting config value:'
                    f' key={key}; value={value}; type={type_str}')
                raise exc
            sql = self.sql_set_key(key, value)
            logger.info("SQL SET KEY:\n" + sql)
        self.execute(sql)

    def rm(self, key):
        """Remove a config key from the database."""
        self.execute(self.sql_rm_key(key))

    def table_exists(self, name):
        """Return True if table exists in DB."""
        return name in self.sql_get_tables()

    def log_data(self, data):
        """Write current readings to the database."""
        dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + "+10"
        data['datetime'] = dt
        try:
            self.execute(self.sql_write_datalog(data))
        except Exception as exc:
            logger.error(
                f"DB.log_data: exception writing to database:\n{exc}")

    # Assertions
    # -------------------------------------------------------------------------

    def _assert_schema(self):
        """Ensure that tables match config."""
        try:
            self.execute(self.sql_get_table_columns(
                self.CONFIG_TABLE_NAME,
                columns=(self.CONFIG_KEY_FIELD, self.CONFIG_VALUE_FIELD)))
        except Exception as exc:
            raise SchemaError(
                "Could not establish config table from database:\n"
                f"CONFIG_VALUE_FIELD: {self.CONFIG_VALUE_FIELD}\n"
                f"CONFIG_KEY_FIELD: {self.CONFIG_KEY_FIELD}\n"
                f"CONFIG_TABLE_NAME: {self.CONFIG_TABLE_NAME}"
                f"\nException:\n{exc}")
        try:
            sql = self.sql_get_table_columns(
                self.DATALOG_TABLE_NAME,
                columns=['id'])
            self.execute(sql)
        except Exception as exc:
            msg = (
                "Could not establish datalog table from database:\n"
                f"DATALOG_TABLE_NAME: {self.DATALOG_TABLE_NAME}")
            if 'no such column' in str(exc):
                msg += "\n\nColumn mismatch. See error above from sqlite3."
            raise ValueError(msg)

    # SQL generation
    # -------------------------------------------------------------------------

    def get_sql_value_type(self, key, value):
        """Return value SQL string and type."""
        type_str = self.get_key_type(key) or type(value).__name__
        assert type_str in TYPECAST, (
            "Config value type not recognised.\n"
            f"{key}: {type_str}")
        if type_str == 'str':
            value = f"'{value}'"
        if type_str == 'bool':
            if str(value).lower() in ('true', '1'):
                value = 1
            else:
                value = 0
        if type_str == 'int':
            value = int(value)
        if type_str == 'float':
            value = float(value)
        return value, type_str

    def get_key_type(self, key):
        """Return type of config key from database."""
        r = self.select(self.sql_get_key(key))
        if r:
            v, type_str = r[0]
            return type_str

    def sql_add_key(self, key, value):
        """Generate SQL to add a new config key: value pair."""
        value, value_type = self.get_sql_value_type(key, value)
        return (
            f"""
            INSERT into {self.CONFIG_TABLE_NAME}
            (
                {self.CONFIG_KEY_FIELD},
                {self.CONFIG_VALUE_FIELD},
                {self.CONFIG_TYPE_FIELD}
            )
            VALUES ('{key}', {value}, '{value_type}')
            """
        )

    def sql_get_key(self, key):
        """Generate SQL to fetch value for config key."""
        return (
            f"""
            SELECT {self.CONFIG_VALUE_FIELD}, {self.CONFIG_TYPE_FIELD}
            from {self.CONFIG_TABLE_NAME}
            WHERE {self.CONFIG_KEY_FIELD} = '{key}'
            """
        )

    def sql_set_key(self, key, value):
        """Generate SQL to fetch value for config key."""
        value, value_type = self.get_sql_value_type(key, value)
        return (
            f"""
            UPDATE {self.CONFIG_TABLE_NAME}
            SET {self.CONFIG_VALUE_FIELD} = {value},
                {self.CONFIG_TYPE_FIELD} = '{value_type}'
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

    def sql_write_datalog(self, data):
        """Generate SQL to write row on datalog table."""
        def get_sql_str(field):
            """Return field (name, object) as SQL string."""
            col, val = field
            if col == 'datetime':
                return f"'{val}'"
            if val is None:
                return "NULL"
            return val

        fields = data.items()
        columns = [x[0] for x in fields]
        values = [
            get_sql_str(f) for f in fields
        ]

        return (
            f"""
            INSERT INTO {self.DATALOG_TABLE_NAME}
            ({', '.join(columns)})
            VALUES ({",".join([str(x) for x in values])})
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
