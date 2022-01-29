"""Perform a sweep of all parameters and apply corrections as necessary."""

try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

import logging
from time import sleep

from hydropi.config import config
from hydropi.process import check
from hydropi.notifications import telegram
from hydropi.interfaces import PipeTemperatureSensor

logger = logging.getLogger('hydropi')


def sweep():
    """Perform sweep, log readings and adjust."""
    try:
        while True:
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
            sleep(60 * config.SWEEP_CYCLE_MINUTES)
    except Exception as exc:
        telegram.notify(f"ERROR ENCOUNTERED IN MAINTENANCE SWEEP:\n\n{exc}")
        raise exc
    finally:
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
        else:
            io.cleanup()
