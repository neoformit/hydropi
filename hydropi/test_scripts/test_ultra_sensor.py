#!/usr/bin/env python3

"""Test ultrasonic sensor.

https://pimylifeup.com/raspberry-pi-distance-sensor/

5cm from parallel wall it is accurate to within 10mm.

"""

import time
import RPi.GPIO as GPIO

PIN_TRIGGER = 4
PIN_ECHO = 5


def setup():
    """Configure ultrasonic sensor."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    # Let sensor settle
    time.sleep(2)


def read():
    """Take a distance reading."""
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)

    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    return round(pulse_duration * 17150 * 10)


if __name__ == '__main__':
    print("Measuring distance")
    try:
        setup()
        while True:
            print(f"Read: {read()}mm")
    finally:
        GPIO.cleanup()
