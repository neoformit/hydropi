"""Check pH level."""

import logging
from threading import Thread

from hydropi.config import config
from hydropi.interfaces.sensors.ph import PHSensor
from hydropi.interfaces.controllers.ph import PHController
from hydropi.errors import handle_errors

logger = logging.getLogger('hydropi')


@handle_errors
def level():
    """Check nutrient levels."""
    sensor = PHSensor()
    stat = sensor.read()

    # Not yet capable of maintenance
    return stat

    # Need to refactor to use database history and take action based on median
    # levels over past hour. This prevents responding to spurious (spike)
    # measurements - like when additions have just been mixed into the tank!

    if config.PH_ACTION_THRESHOLD > abs(stat - config.PH_TARGET):
        logger.info(f"pH within acceptable range of target {config.PH_TARGET}")
        return stat
    return restore(stat)


def restore(stat):
    """Evaluate pH levels and take action to restore."""
    if (stat - config.PH_TARGET) < 0:
        logger.warning("PH TOO LOW: CANNOT TAKE ACTION")
        return stat
    logger.info("pH too low: performing ph reduction")
    ph = PHController()
    Thread(ph.down).start()
    return stat
