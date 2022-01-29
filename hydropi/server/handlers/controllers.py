"""Handlers for interacting with controllers."""

from threading import Thread

from hydropi import interfaces
from hydropi.process import pause


def action(name, action):
    """Perform an action on the given controller."""
    controller = interfaces.CONTROLLERS[name]()
    target = getattr(controller, action['method'])
    Thread(target=target, kwargs=action.get('kwargs')).start()


def set_pause(state):
    """Enable and disable service pause."""
    pause.set(state)
