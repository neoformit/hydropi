"""Route requests to HydroPi services."""

import json
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


class Response:
    """Loose representation of a request."""

    def __init__(self, status, data=None):
        """Create response instance."""
        self.status = status
        self.content = json.dumps(data or '')


def resolve(method, path):
    """Resolve request URI to handler."""
    request = Request(method=method, path=path)
    route = map.match(request.path)
    if not route:
        raise Http404("Route does not exist")
    controller = getattr(
        controllers,
        route['controller'].title() + "Controller")
    if hasattr(controller, request.method.lower()):
        return Response(
            200,
            getattr(controller, request.method.lower())(request))
    raise Http400("Method not allowed for this route")
