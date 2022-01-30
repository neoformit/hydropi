"""Handlers for interacting with controllers."""

import logging
from threading import Thread

from hydropi import interfaces
from hydropi.process import pause

logger = logging.getLogger('hydropi')


def action(name, action):
    """Perform an action on the given controller."""
    method = action['method']
    controller = interfaces.CONTROLLERS[name]()
    if method == 'on':
        return controller.on(abandon=True)
    target = getattr(controller, method)
    Thread(target=target, kwargs=action.get('kwargs')).start()


def set_pause(state):
    """Enable and disable service pause."""
    pause.set(state)
