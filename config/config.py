"""Hardware configuration.

These are default values that may be overwritten at runtime.

- Digital io passes through pins (gpio header pins)
- Analogue io passes through channels (MCP3008 chip interface)

Perhaps makes sense to conditionally read/set config from SQLite connection at
runtime, if one exists. Can share a connection with the web app. But need to
access config through an interface `config.get(PARAM)` for this to work
properly.
"""

from .db import DB


DATABASE = {
    # 'SQLITE_PATH': 'db.sqlite',
    # 'TABLE_NAME': 'dash_config',
}

DEFAULTS = {

    # Pins
    #-------------------------------------------------------------------------------

    # Inputs
    'CHANNEL_PH': 1,
    'CHANNEL_EC': 2,
    'CHANNEL_PRESSURE': 3,
    'PIN_DEPTH_TRIG': 4,
    'PIN_DEPTH_ECHO': 5,

    # Outputs
    'PIN_PRESSURE_PUMP': 6,
    'PIN_PRESSURE_FLOW': 7,
    'PIN_EC_UP_PUMP': 8,
    'PIN_PH_DOWN_PUMP': 9,
    'PIN_WATER_FLOW': 10,

    # Parameters
    #-------------------------------------------------------------------------------

    # Cycle durations
    'SWEEP_CYCLE_MINUTES': 15,
    'MIST_CYCLE_MINUTES': 5,
    'MIST_DURATION_SECONDS': 15,

    # Pressure monitoring
    'MIN_PRESSURE': None,
    'MAX_PRESSURE': None,
    'PUMP_LAST_RUN': "19:45",
    'PUMP_SILENT_BEFORE': "07:00",
    'PUMP_SILENT_AFTER': "20:00",

    # PH monitoring
    'PH_TARGET': 6.0,
    'PH_LIMIT_WARN': 0.5,
    'PH_LIMIT_DANGER': 1,
    'PH_ACTION_TOLERANCE': 0.25,
    'PH_ACTION_TOLERANCE': 10,

    # EC monitoring
    'EC_TARGET': 1.8,
    'EC_LIMIT_WARN': 0.4,
    'EC_LIMIT_DANGER': 1,
    'EC_ACTION_TOLERANCE': 0.2,

    # Water level monitoring
    'DEPTH_UNIT': 'mm',
    'DEPTH_MAXIMUM_unit': None,       # Machine units when full (e.g. 200mm)
    'DEPTH_TARGET': 1.0,              # Full
    'DEPTH_LIMIT_WARN': 0.75,         # 75%
    'DEPTH_LIMIT_DANGER': 0.5,
    'DEPTH_ACTION_TOLERANCE': 0.75,
}


def get(key):
    """Return config value for key."""
    if not DATABASE:
        return DEFAULTS[key]
    db = DB()
    return db.get(key) or DEFAULTS[key]
