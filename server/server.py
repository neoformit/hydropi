"""Run a local HTTP server over a socket.

Listen for instructions from other processes.
"""

from socket import (
    socket,
    AF_INET,
    SOCK_STREAM,
    SO_REUSEADDR,
    SOL_SOCKET
)

from config import config
from . import routes

HOST, PORT = "127.0.0.1", config.DAEMON_HTTP_PORT
SOCKET_OPT_VALUE = 1
BUFFER_MAX_BYTES = 4096
CONNECTION_MAX_BACKLOG = 1


def listen():
    """Handle incoming requests."""
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, SOCKET_OPT_VALUE)
        sock.bind((HOST, PORT))
        sock.listen(CONNECTION_MAX_BACKLOG)
        while True:
            try:
                client, address = sock.accept()
                request = client.recv(BUFFER_MAX_BYTES).decode()
                method, path = request.split('\r\n')[0].split(' ')[:2]
                print(f"REQUEST METHOD: {method}")
                print(f"REQUEST PATH: {path}")
                response = routes.resolve(method, path)
                client.sendall(response_success(response))
            except Exception as exc:
                client.sendall(response_error(exc))
            finally:
                client.close()


def response_success(response):
    """Render HTTP error response from exception."""
    print("RESPONSE SUCCESS")
    code = "OK"
    http_response = (
        f"HTTP/1.1 {response.status} {code}\n"
        "Content-Type: application/json\n\n"
        f"{response.content}\n"
    )
    print(f"Response:\n{http_response}")
    return bytes(http_response, 'utf-8')


def response_error(exc=None):
    """Render HTTP error response from exception."""
    if exc:
        content = f"{exc.__class__.__name__}: {exc}"
    else:
        content = "Server Error"
    print(f"RESPONSE ERROR:\n{content}")
    code = "Server error"
    status_code = getattr(exc, 'status', 500)
    response = (
        f"HTTP/1.1 {status_code} {code}\n"
        "Content-Type: text/plain\n\n"
        f"{content}\n"
    )
    print(f"Response:\n{response}")
    return bytes(response, 'utf-8')
