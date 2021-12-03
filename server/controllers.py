"""Client-facing HydroPi services."""

import json
import process
import interfaces


class IndexController:
    """Handle root requests."""

    def get(request):
        """Return hydro status."""
        return json.dumps({
            'ph': 5.65,
            'ec': 2.16,
            'depth': 0.96,
            'temperature': 26.3,
            'pressure': 124,
        })
