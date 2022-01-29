"""Control pausing of hydropi services."""

import os

from hydropi.config import config

FLAG_PATH = os.path.join(config.TEMP_DIR, 'pause.flag')


def paused():
    """Determine if currently paused."""
    return os.path.exists(FLAG_PATH)


def set(state):
    """Set pause on/off."""
    if state:
        with open(FLAG_PATH, 'w') as f:
            f.write("Flag hydropi services as paused\n")
    else:
        if os.path.exists(FLAG_PATH):
            os.remove(FLAG_PATH)
