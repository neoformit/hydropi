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
)

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
    # This doesn't make sense
    return
    
    for C in CONTROLLERS.values():
        C.__del__(None)
