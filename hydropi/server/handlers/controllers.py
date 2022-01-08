"""Handlers for interacting with controllers."""

from threading import Thread

from hydropi import interfaces


def action(name, action):
    """Perform an action on the given controller."""
    controller = interfaces.CONTROLLERS[name]()
    target = getattr(controller, action['action'])
    Thread(target=target, args=action['args'], kwargs=action['kwargs']).start()
