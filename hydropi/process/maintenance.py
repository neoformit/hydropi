"""Perform a sweep of all parameters and apply corrections as necessary."""

try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

import logging
from time import sleep
from threading import Thread

from hydropi.config import config
from hydropi.process import check
from hydropi.process.errors import ErrorWatcher
from hydropi.interfaces import PipeTemperatureSensor
from hydropi.interfaces import MixPumpController
from .pause import paused

logger = logging.getLogger('hydropi')


def sweep():
    """Perform sweep, log readings and adjust."""
    minutes_without_mix = 0
    try:
        ew = ErrorWatcher()
        try:
            while True:
                if paused():
                    logger.info("MAINTENANCE PAUSED: Skipping sweep round")
                    sleep(60 * config.SWEEP_CYCLE_MINUTES)
                else:
                    sweep_and_restore()
                    sleep(60 * config.SWEEP_CYCLE_MINUTES)
                    if minutes_without_mix >= config.MIX_EVERY_MINUTES:
                        # Run mix pump to aerate nutrients
                        Thread(target=MixPumpController().mix).start()
                        minutes_without_mix = 0
                    else:
                        minutes_without_mix += config.SWEEP_CYCLE_MINUTES
                ew.reset()
        except Exception as exc:
            ew.catch(exc, message="ERROR ENCOUNTERED IN MAINTENANCE")
    finally:
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
        else:
            io.cleanup()


def sweep_and_restore():
    """Perform parameter check and balance."""
    temp = PipeTemperatureSensor()
    stat = {
        'ec': check.ec.level(),
        'ph': check.ph.level(),
        'volume_l': check.tank.depth(),
        'pressure_psi': check.pressure.level(),
        'temp_c': temp.read(),
    }
    if config.db:
        config.db.log_data(stat)
