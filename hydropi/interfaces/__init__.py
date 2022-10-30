"""Initialize hardware interfaces for consumption."""

from .sensors import (
    ECSensor,
    PHSensor,
    DepthSensor,
    PressureSensor,
    TankTemperatureSensor,
    PipeTemperatureSensor,
)
from .controllers import (
    ECController,
    PHController,
    MistController,
    MixPumpController,
    WaterController,
    PressurePumpController,
    clean,
)
from .controllers import clean

SENSORS = {
    'ec': ECSensor,
    'ph': PHSensor,
    'depth': DepthSensor,
    'pressure': PressureSensor,
    'temperature': TankTemperatureSensor,
}

CONTROLLERS = {
    'ec': ECController,
    'ph': PHController,
    'mist': MistController,
    'mix': MixPumpController,
    'water': WaterController,
    'pressure': PressurePumpController,
}


def cleanup():
    """Clean up on termination."""
    controllers.clean.deeds()

    # This doesn't make sense until we have sensible __del__ methods:
    # for C in CONTROLLERS.values():
    #     C.__del__(None)
