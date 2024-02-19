#!/usr/bin/env python3
import sys
import time

from icp10125 import ICP10125

"""QNH for calculating altitude.
This value is the atmospheric pressure reference used to calculate altitude.
The default value is 1013.25, but you *must* get a value from your local airport
or weather reports for a remotely accurate altitude!

Edit this value or run with ./bargraph <your QNH>
"""
QNH = 1013.25

if len(sys.argv) > 1:
    QNH = float(sys.argv[1])

if QNH == 1013.25:
    print("""QNH is set to the default of 1013.25. Altitude may not be accurate!

Try ./bargraph.py <your QNH>
""")


def calculate_altitude(pressure, qnh=1013.25):
    return 44330.0 * (1.0 - pow(pressure / qnh, (1.0 / 5.255)))


device = ICP10125()

try:
    while True:
        pressure, temperature = device.measure()
        altitude = calculate_altitude(pressure / 100, qnh=QNH)
        print(f"""Pressure: {pressure / 100:.2f}hPa
Temperature: {temperature:.4f}c
Altitude:    {altitude:.4f}m
""")
        time.sleep(1.0)
except KeyboardInterrupt:
    pass
