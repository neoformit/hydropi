"""Generic handlers for status, log files etc."""

import os

from hydropi.config import config, STATUS
from hydropi.interfaces.sensors import (
    DepthSensor,
    PressureSensor,
    ECSensor,
    # PHSensor,
    # TemperatureSensor,
)

SENSORS = {
    'pressure': PressureSensor,
    'depth': DepthSensor,
    'ec': ECSensor,
    # 'ph': PHSensor,
    # 'temperature': TemperatureSensor,
}


def get_status():
    """Return current status as data."""
    params = {
        k: v.get_status()
        for k, v in SENSORS.items()
    }
    status_list = [
        v['status']
        for v in params.values()
    ]
    if STATUS.DANGER in status_list:
        status = STATUS.DANGER
    elif STATUS.WARNING in status_list:
        status = STATUS.WARNING
    else:
        status = STATUS.NORMAL

    return {
        'params': params,
        'text': status,
    }


def get_logs():
    """Return most recent log output."""
    MAX_BYTES = 1024 * 1024  # 1MB
    fname = os.path.join(config.CONFIG_DIR, 'hydro.log')
    with open(fname, 'rb') as f:
        if os.path.getsize(fname) > MAX_BYTES:
            # Open the last MB only
            f.seek(-1 * MAX_BYTES, os.SEEK_END)
        lines = f.read().decode('utf-8').split('\n')
    lines.reverse()
    if len(lines) < 150:
        return '\n'.join(lines) + '\n'
    return '\n'.join(lines[:150]) + '\n'
