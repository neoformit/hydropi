"""Read temp from OneWire interface."""

from time import sleep

DEVICE = '/sys/bus/w1/devices/28-01131b576dcc/w1_slave'


def read():
    """Read temperature."""
    with open(DEVICE) as f:
        data = f.read().split('\n')[1].split('t=')[1]
    return int(data) / 1000


if __name__ == '__main__':
    while True:
        print("Reading: %.1f°C" % read())
        sleep(1)
