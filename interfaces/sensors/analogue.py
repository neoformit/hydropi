"""Utilities for reading sensor input.

pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-mcp3xxx

See https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi
"""

import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


class AnalogueInterface:

    def __init__(self, channel):
        """Build interface to MCP3008 chip.

        Pass the required channel and request readings with ai.read().
        """
        SPI = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        CS = digitalio.DigitalInOut(board.D22)
        MCP = MCP.MCP3008(spi, cs)

        # Create analog input channels
        self.interface = AnalogIn(mcp, eval(f"MCP.P{channel}"))  # Should use getattr here

    def read():
        """Return channel reading."""
        return self.interface.value
