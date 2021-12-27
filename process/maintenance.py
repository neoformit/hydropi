"""Perform a sweep of all parameters and apply corrections as necessary."""

from time import sleep

from config import config
# from interfaces.sensors import thermometer
from process import check


def sweep():
    """Perform sweep, log readings and adjust."""
    while True:
        stat = {
            # 'ec': check.ec.level(),
            # 'ph': check.ph.level(),
            # 'depth_mm': check.tank.depth(),
            'pressure_psi': check.pressure.level(),
            # 'temp_c': thermometer.read(),
        }
        if config.db:
            config.db.log_data(stat)
        sleep(60 * config.SWEEP_CYCLE_MINUTES)
