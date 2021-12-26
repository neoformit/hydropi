"""Check the nutrient pressure tank level and adjust with pressure pump."""

import time
import logging
from threading import Thread

import notifications
from config import config
from interfaces.sensors.pressure import PressureSensor
from interfaces.controllers.pressure import PressurePumpController

logger = logging.getLogger(__name__)


def level():
    """Check pressure level."""
    sensor = PressureSensor()
    stat = sensor.read(n=5)
    logger.info(f"READ pressure: {stat} {sensor.UNIT}")

    if stat < config.ALERT_PRESSURE_PSI:
        message = f"Tank pressure below ALERT level: {stat} {sensor.UNIT}"
        logger.warning(message)
        notifications.alert(message)

    if stat > config.MIN_PRESSURE_PSI:
        logger.debug(
            "Tank pressure above lower limit of"
            f" {config.MIN_PRESSURE_PSI} {sensor.UNIT}"
        )
        return stat
    return restore(stat)


def restore(stat):
    """Evaluate tank pressure and take action to restore."""
    if is_quiet_time():
        logger.info(
            "Tank pressure low: waiting for quiet time end to restore.")
        return

    logger.info("Tank pressure low: restoring pressure.")
    pump = PressurePumpController()
    Thread(pump.refill).start()
    return stat


def is_quiet_time():
    """Check whether we are currently in quiet time."""
    now = time.now()
    quiet_start = time.strptime("%H:%M", config.QUIET_TIME_START)
    quiet_end = time.strptime(config.QUIET_TIME_END)
    if now > quiet_start or now < quiet_end:
        return True
    return False
