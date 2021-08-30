"""Monitor hydroponics system to maintain state."""

import time
from threading import Thread

from config import config
import process


def main():
    """Monitor and maintain the system."""
    Thread(target=process.mist).start()
    Thread(target=process.sweep).start()
