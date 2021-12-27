"""Quick access controllers for CLI use."""

import sys
from ..sensors.ec import ECSensor
from ..sensors.ph import PHSensor
from ..sensors.depth import DepthSensor
from ..sensors.pressure import PressureSensor
from ..sensors.temperature import TemperatureSensor

from ..controllers.ec import ECController
from ..controllers.ph import PHController
from ..controllers.mist import MistController
from ..controllers.mix import MixPumpController
from ..controllers.water import WaterController
from ..controllers.pressure import PressurePumpController

assert sys.stdin and sys.stdin.isatty(), "Shortcuts are for CLI use only"

pc = PressurePumpController()
mc = MistController()
ps = PressureSensor()
