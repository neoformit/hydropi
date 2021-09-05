"""Perform a sweep of all parameters and apply corrections as necessary."""

from config import config

from . import check


def sweep():
    """Perform sweep, log readings and adjust."""
    # TODO: Check that these functions are non blocking
    stat = {}
    stat['ec'] = check.ec.level()
    stat['ph'] = check.ph.level()
    stat['tank'] = check.tank.depth()
    stat['pressure'] = check.pressure.level()
    config.db.write_stat(stat)
