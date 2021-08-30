"""Hardware configuration.

These are default values that may be overwritten at runtime.

- Digital io passes through pins (gpio header pins)
- Analogue io passes through channels (MCP3008 chip interface)

Perhaps makes sense to conditionally read/set config from SQLite connection at
runtime, if one exists. Can share a connection with the web app. But need to
access config through an interface `config.get(PARAM)` for this to work
properly.
"""

import yaml
from types import SimpleNamespace

from .db import DB


DATABASE = {
    # 'SQLITE_PATH': 'db.sqlite',
    # 'TABLE_NAME': 'dash_config',
}

with open('config.yaml') as f:
    DEFAULTS = yaml.safe_load(f)

# Create default config
config = SimpleNamespace(**DEFAULTS)
db = DB()

# Override with database values if present
if DATABASE:
    db_keys = {
        db.get(DEFAULTS[key])
        for key in DEFAULTS
        if db.get(DEFAULTS[key])
    }
    config.update(db_keys)
