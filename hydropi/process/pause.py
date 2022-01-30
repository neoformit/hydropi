"""Control pausing of hydropi services."""

import os
import logging

from hydropi.config import config

logger = logging.getLogger('hydropi')

FLAG_PATH = os.path.join(config.TEMP_DIR, 'pause.flag')


def paused():
    """Determine if currently paused."""
    return os.path.exists(FLAG_PATH)


def set(state):
    """Set pause on/off."""
    if state:
        logger.debug("ACTION: set paused ON")
        with open(FLAG_PATH, 'w') as f:
            f.write("Flag hydropi services as paused\n")
        # Could do a GPIO.cleanup() here to REALLY stop everything?
    else:
        logger.debug("ACTION: set paused OFF")
        if os.path.exists(FLAG_PATH):
            os.remove(FLAG_PATH)
