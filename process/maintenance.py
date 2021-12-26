"""Perform a sweep of all parameters and apply corrections as necessary."""

from config import config

from interfaces.sensors import thermometer
from process import check


def sweep():
    """Perform sweep, log readings and adjust."""
    stat = {
        'ec': check.ec.level(),
        'ph': check.ph.level(),
        'depth_mm': check.tank.depth(),
        'pressure_psi': check.pressure.level(),
        'temp_c': thermometer.read(),
    }
    config.db.log_data(stat)
