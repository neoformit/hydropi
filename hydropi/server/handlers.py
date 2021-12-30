"""Utilities for interacting with the system."""

import os

from hydropi.config import config
from hydropi.interfaces.sensors import (
    DepthSensor,
    # PHSensor,
    # ECSensor,
    PressureSensor,
    # TemperatureSensor,
)

SENSORS = {
    # 'depth': DepthSensor,
    # 'ph': PHSensor,
    # 'ec': ECSensor,
    # 'temperature': TemperatureSensor,
    'pressure': PressureSensor,
}


def get_status():
    """Return current status as data."""
    params = {
        k: v.get_status()
        for k, v in SENSORS.items()
    }
    status = 'normal'
    if 'warning' in params.values():
        status = 'warning'
    if 'danger' in params.values():
        status = 'danger'

    # Hard code fake depth until that's working
    params['depth'] = {
        'text': 'Depth',
        'status': 'normal',
        'value': 30,
        'percent': 0.45,
        'unit': '%',
      }
    return {
        'params': params,
        'text': status,
    }


def get_log():
    """Return most recent log output."""
    fname = os.path.join(config.CONFIG_DIR, 'hydro.log')
    with open(fname) as f:
        lines = f.read().split('\n')
    if len(lines) < 50:
        return '\n'.join(lines) + '\n'
    return '\n'.join(lines)[-50:] + '\n'
