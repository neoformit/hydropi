"""Config to expose for configuration in web app."""

EXPOSED_CONFIG = {
    'general': (
        {
            'key': 'QUIET_TIME_START',
            'type': 'text',
            'help': 'Time of evening when pump should no longer run (HH:MM)',
        },
        {
            'key': 'QUIET_TIME_END',
            'type': 'text',
            'help': 'Time of morning when pump can resume operation (HH:MM)',
        },
        {
            'key': 'SWEEP_CYCLE_MINUTES',
            'type': 'number',
            'help': 'Interval between status check and balance (minutes)',
        },
    ),
    'mist': (
        {
            'key': 'MIST_CYCLE_MINUTES',
            'type': 'number',
            'help': 'Interval between mist release (minutes)',
        },
        {
            'key': 'MIST_CYCLE_NIGHT_MINUTES',
            'type': 'number',
            'help': 'Interval while misting during quiet time (minutes)',
        },
        {
            'key': 'MIST_DURATION_SECONDS',
            'type': 'number',
            'help': 'Duration of each mist release (seconds)',
        },
    ),
    'ec': (
        {
            'key': 'EC_MIN',
            'type': 'number',
            'help': ('Lower limit of target EC range (μS)'),
        },
        {
            'key': 'EC_MAX',
            'type': 'number',
            'help': ('Upper limit of target EC range (μS)'),
        },
        {
            'key': 'EC_ADDITION_ML',
            'type': 'number',
            'help': ('Volume of nutrient to deliver before mix and re-check'
                     ' (ml). 30ml per 10L tap water.'),
        },
    ),
    'ph': (
        {
            'key': 'PH_MIN',
            'type': 'number',
            'help': 'Lower limit of target pH range',
        },
        {
            'key': 'PH_MAX',
            'type': 'number',
            'help': 'Upper limit of target pH range',
        },
        {
            'key': 'PH_ADDITION_ML',
            'type': 'number',
            'help': ('Volume of pH-down to deliver before mix and re-check'
                     ' (ml). 5ml per 10L tap water.'),
        },
    ),
    'mix': (
        {
            'key': 'MIX_PUMP_SECONDS',
            'type': 'number',
            'help': ('Duration of mixing after a nutrient tank addition'
                     ' (seconds)'),
        },
        {
            'key': 'MIX_ADDITION_DELAY_SECONDS',
            'type': 'number',
            'help': 'Duration of mixing before an addition is made (seconds)',
        },
        {
            'key': 'MIX_EVERY_MINUTES',
            'type': 'number',
            'help': 'Interval between nutrient tank mixing (minutes)',
        },
    ),
    'depth': (
        {
            'key': 'VOLUME_TARGET_L',
            'type': 'number',
            'help': 'Target volume for the nutrient tank (litres)',
        },
        {
            'key': 'VOLUME_TOLERANCE',
            'type': 'number',
            'help': 'Accepted deviation from target volume (proportion)',
        },
        {
            'key': 'WATER_ADDITION_SECONDS',
            'type': 'number',
            'help': ('Duration of water addition before re-measurement of tank'
                     ' depth (seconds)'),
        },
        {
            'key': 'WATER_MAX_ADDITION_SECONDS',
            'type': 'number',
            'help': ('Maximum duration of water delivery in one sweep event'
                     ' - this is a failsafe against accidental flooding'
                     ' (seconds)'),
            },
    ),
    'pressure': (
        {
            'key': 'MIN_PRESSURE_PSI',
            'type': 'number',
            'help': 'Threshold tank pressure to trigger a refill (PSI)',
        },
        {
            'key': 'MAX_PRESSURE_PSI',
            'type': 'number',
            'help': 'Tank pressure where refill will terminate (PSI)',
        },
        {
            'key': 'PRESSURE_REFILL_DURATION_SECONDS',
            'type': 'number',
            'help': (
                'Estimated duration of a tank refill from min to max'
                ' (seconds)'),
        },
    ),
}
