"""Monitor hydroponics system to maintain state.

Pass database parameters to enable real-time configuration.
"""

import time
from threading import Thread

from process.delivery import mist
from process.maintenance import sweep


def cycle():
    """Monitor and maintain the system."""
    Thread(target=process.mist).start()
    Thread(target=process.sweep).start()


if __name__ == '__main__':
    cycle()
