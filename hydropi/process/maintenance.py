"""Perform a sweep of all parameters and apply corrections as necessary."""

from time import sleep

from hydropi.config import config
from hydropi.interfaces import PipeTemperatureSensor
from hydropi.process import check


def sweep():
    """Perform sweep, log readings and adjust."""
    while True:
        temp = PipeTemperatureSensor()
        stat = {
            'ec': check.ec.level(),
            'ph': check.ph.level(),
            'depth_l': check.tank.depth(),
            'pressure_psi': check.pressure.level(),
            'temp_c': temp.read(),
        }
        if config.db:
            config.db.log_data(stat)
        sleep(60 * config.SWEEP_CYCLE_MINUTES)
