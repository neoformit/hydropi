"""Hardware configuration.

Constants prefixed with DEFAULT_ will be overridden by database values, if they
exist.
"""

# Pins
#-------------------------------------------------------------------------------

# Inputs
PIN_PH = 1
PIN_EC = 2
PIN_DEPTH = 3
PIN_PRESSURE = 4

# Outputs
PIN_PUMP = 5
PIN_FLOW = 6

# Parameters
#-------------------------------------------------------------------------------

# Minutes between status checks
SWEEP_CYCLE_MINUTES = 5

# Pressure monitoring
MIN_PRESSURE = None
MAX_PRESSURE = None
PUMP_LAST_RUN = "19:45"
PUMP_SILENT_BEFORE = "07:00"
PUMP_SILENT_AFTER = "20:00"

# PH monitoring
PH_TARGET = 6.0
PH_LIMIT_WARN = 0.5
PH_LIMIT_DANGER = 1
PH_ACTION_TOLERANCE = 0.25
PH_ACTION_TOLERANCE = 10

# EC monitoring
EC_TARGET = 1.8
EC_LIMIT_WARN = 0.4
EC_LIMIT_DANGER = 1
EC_ACTION_TOLERANCE = 0.2

# Water monitoring
DEPTH_UNIT_HUMAN = 'mm'
DEPTH_UNIT_MACHINE = 'psi'
DEPTH_MACHINE_TO_HUMAN = None
DEPTH_MAXIMUM_unit = None       # Machine units when full (e.g. 200mm)
DEPTH_TARGET = 1.0              # Full
DEPTH_LIMIT_WARN = 0.75         # 75%
DEPTH_LIMIT_DANGER = 0.5
DEPTH_ACTION_TOLERANCE = 0.75
