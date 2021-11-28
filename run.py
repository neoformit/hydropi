#!/usr/bin/env python3

"""Monitor hydroponics system to maintain state.

Pass database parameters to enable real-time configuration.
"""

try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None
from threading import Thread
from argparse import ArgumentParser
from importlib import import_module

from process.delivery import mist
from process.maintenance import sweep

import signal
signal.signal(signal.SIGINT, signal.default_int_handler)


def main():
    """Monitor and maintain the system."""
    try:
        Thread(target=mist).start()
        Thread(target=sweep).start()
    finally:
        io.cleanup()


def get_args():
    """Parse command line arguments."""
    ap = ArgumentParser(description='Process some integers.')
    ap.add_argument(
        '--test',
        dest='test_component',
        type=str,
        help="Test an interface class",
    )
    return ap.parse_args()


def test(component):
    """Test the given interface class."""
    module, classname = component.rsplit('.', 1)
    m = import_module(module)
    C = getattr(m, classname)
    obj = C()
    if not hasattr(obj, 'test'):
        raise AttributeError(
            f"Failed: Class '{component}' has no test method."
            " Add a test method to make this class testable."
        )
    obj.test()


if __name__ == '__main__':
    try:
        args = get_args()
        if args.test_component:
            test(args.test_component)
        else:
            main()
    finally:
        io.cleanup()
