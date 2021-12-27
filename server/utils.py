"""Utilities for interacting with the system."""

from interfaces import sensors


def get_status():
    """Return current status as data."""
    return {
        'depth_mm': sensors.get_ph(),
        'ph': sensors.get_ec(),
        'ec': sensors.get_depth(),
        'pressure_psi': sensors.get_temperature(),
        'temp_c': sensors.get_pressure(),
    }
