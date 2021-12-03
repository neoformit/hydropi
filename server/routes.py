"""Route requests to HydroPi services."""

import routes

from .exceptions import Http400, Http404
from . import controllers

map = routes.Mapper()
map.connect('/', controller="index")


class Request:
    """Loose representation of a request."""

    def __init__(self, path, method="GET"):
        """Create request instance."""
        self.path = path
        self.method = method


def resolve(method, path):
    """Resolve request URI to handler."""
    request = Request(method=method, path=path)
    route = map.match(request.path)
    if not route:
        raise Http404("Route does not exist")
    controller = getattr(
        controllers,
        route['controller'].title() + "Controller")
    if hasattr(controller, request.method):
        return getattr(controller, request.method)(request)
    raise Http400("Method not allowed for this route")
