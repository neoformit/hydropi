"""Monitor hydroponics system to maintain state.

Pass database parameters to enable real-time configuration.
"""

from threading import Thread
from argparse import ArgumentParser
from importlib import import_module

from process.delivery import mist
from process.maintenance import sweep


def cycle():
    """Monitor and maintain the system."""
    Thread(target=mist).start()
    Thread(target=sweep).start()


def get_args():
    """Parse command line arguments."""
    ap = ArgumentParser(description='Process some integers.')
    ap.add_argument(
        '--test-component',
        dest='component',
        type=str,
        help="Test an interface class",
    )
    return ap.parse_args()


def test(component):
    """Test the given interface class."""
    C = import_module(component)
    obj = C()
    if not getattr(obj, 'test'):
        raise AttributeError(
            f"Failed: Object '{component}' has no test method.")
    obj.test()


if __name__ == '__main__':
    args = get_args()
    if args.test_component:
        test(args.test_component)
    else:
        cycle()
