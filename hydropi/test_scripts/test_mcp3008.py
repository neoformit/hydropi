"""Test MCP3008 analog-digital converter with software SPI."""

import time
from Adafruit_MCP3008 import MCP3008


CLK = 11
MISO = 9
MOSI = 10
CS = 8
CHANNEL = 0

ZERO_OFFSET = -0.0966796875
PSI_MAX = 145

mcp = MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

while True:
    bits = mcp.read_adc(CHANNEL)
    p = bits / 1024 + ZERO_OFFSET
    psi = p * PSI_MAX
    print(f"Pressure: {round(psi, 1)} psi  |  proportion: {p}")
    time.sleep(0.5)
