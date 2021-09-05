"""Check the nutrient pressure tank level and adjust with pressure pump."""

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
        message = f"Pressure tank below ALERT level: {stat} {sensor.UNIT}"
        logger.warning(message)
        notifications.alert(message)

    if stat > config.MIN_PRESSURE_PSI:
        logger.debug(
            "Tank pressure above acceptable minimum of"
            f" {config.MIN_PRESSURE_PSI} {sensor.UNIT}"
        )
        return stat
    return restore(stat)


def restore(stat):
    """Evaluate tank pressure and take action to restore."""
    logger.info("Tank pressure low: restoring pressure.")
    pump = PressurePumpController()
    Thread(pump.refill).start()
    return stat