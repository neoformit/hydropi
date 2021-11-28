"""Route requests to HydroPi services."""

from . import service


ROUTES = {
    # "/status": service.get_status,
}


def resolve():
    """Resolve request URI to handler."""
    pass
