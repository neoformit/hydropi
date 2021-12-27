"""Utilities for interacting with the system."""

from interfaces.sensors import (
    DepthSensor,
    PHSensor,
    ECSensor,
    PressureSensor,
    TemperatureSensor,
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
