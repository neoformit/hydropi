"""Run a local HTTP server over a socket.

Listen for instructions from other processes.
"""

import json
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM,
    SO_REUSEADDR,
    SOL_SOCKET
)
from requests import Response

from config import config
from . import routes

HOST, PORT = "127.0.0.1", config.DAEMON_HTTP_PORT
SOCKET_OPT_VALUE = 1
BUFFER_MAX_BYTES = 4096
CONNECTION_MAX_BACKLOG = 1


def listen():
    """Listen for requests."""
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, SOCKET_OPT_VALUE)
        sock.bind((HOST, PORT))
        sock.listen(CONNECTION_MAX_BACKLOG)
        while True:
            try:
                client, address = sock.accept()
                request = client.recv(BUFFER_MAX_BYTES).decode()
                method, path = request.split('\r\n')[0].split(' ')[:2]
                print(f"METHOD: {method}")
                print(f"PATH: {path}")
                # data = routes.resolve(method, path)
                # client.sendall(response_success(data))
            except Exception as exc:
                client.sendall(response_error(exc))
            finally:
                client.close()


def response_success(status=None, data=None):
    """Render HTTP error response from exception."""
    r = Response()
    r.code = "Server error"
    r.status_code = status or 500
    r._content = (json.dumps(data) or '').encode()
    return r


def response_error(exc=None):
    """Render HTTP error response from exception."""
    if exc:
        content = f"{exc.__class__}: {exc}"
    else:
        content = "Server error"
    r = Response()
    r.code = "Server error"
    r.status_code = getattr(exc, 'status', None) or 500
    r._content = content.encode()
    return r
