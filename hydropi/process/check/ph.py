"""Check pH level."""

import logging
from threading import Thread

from hydropi.config import config
from hydropi.interfaces.sensors.ph import PHSensor
from hydropi.interfaces.controllers.ph import PHController

logger = logging.getLogger('hydropi')


def level():
    """Check nutrient levels."""
    sensor = PHSensor()
    stat = sensor.read(n=5)
    logger.info(f"READ pH: {stat}{sensor.UNIT}")
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
