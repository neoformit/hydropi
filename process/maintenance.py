"""Perform a sweep of all parameters and apply corrections as necessary."""

# from config import config

from . import check


def sweep():
    """Perform sweep, log readings and adjust."""
    # Check that these functions are not blocking
    stat = {}
    stat['ec'] = check.ec.level()
    stat['ph'] = check.ph.level()
    stat['tank'] = check.tank.depth()
    stat['pressure'] = check.pressure.level()

    # Write current stat to config.db
