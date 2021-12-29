"""Initialize hardware interfaces for consumption."""

from .sensors import (
    ECSensor,
    PHSensor,
    DepthSensor,
    PressureSensor,
    TemperatureSensor,
)
from .controllers import (
    ECController,
    PHController,
    MistController,
    MixPumpController,
    WaterController,
    PressurePumpController,
)

CONTROLLERS = [
    ECController,
    PHController,
    MistController,
    MixPumpController,
    WaterController,
    PressurePumpController,
]


def cleanup():
    """Clean up on termination."""
    for C in CONTROLLERS:
        C.__del__()
