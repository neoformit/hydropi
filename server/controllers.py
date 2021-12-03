"""Client-facing HydroPi services."""

import process
from interfaces import sensors, controllers


class IndexController:
    """Handle root requests."""

    def get(request):
        """Return hydro status."""
        return {
            'ph': sensors.get_ph(),
            'ec': sensors.get_ec(),
            'depth': sensors.get_depth(),
            'temperature': sensors.get_temperature(),
            'pressure': sensors.get_pressure(),
        }
