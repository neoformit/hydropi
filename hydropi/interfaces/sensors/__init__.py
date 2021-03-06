"""Provide a set of interfaces for sensors."""

from .ph import PHSensor
from .ec import ECSensor
from .depth import DepthSensor
from .pressure import PressureSensor
from .temperature import TankTemperatureSensor, PipeTemperatureSensor


def get_ph():
    """Return current pH level."""
    ph = PHSensor()
    return ph.read()


def get_ec():
    """Return current EC (nutrient) level."""
    ec = ECSensor()
    return ec.read()


def get_depth():
    """Return current depth level."""
    ds = DepthSensor()
    return ds.read()


def get_temperature():
    """Return current temperature."""
    ts = TankTemperatureSensor()
    return ts.read()


def get_pressure():
    """Return current pressure."""
    ps = PressureSensor()
    return ps.read()
