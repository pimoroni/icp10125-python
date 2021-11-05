#!/usr/bin/env python3
import sys
from icp10125 import ICP10125, ULTRA_LOW_NOISE

"""QNH for calculating altitude.
This value is the atmospheric pressure reference used to calculate altitude.
The default value is 1013.25, but you *must* get a value from your local airport
or weather reports for a remotely accurate altitude!

Edit this value or run with ./bargraph <your QNH>
"""
QNH = 1013.25

BAR_CHAR = u'\u2588'

ANSI_COLOR_RED = '\x1b[31m'
ANSI_COLOR_GREEN = '\x1b[32m'
ANSI_COLOR_YELLOW = '\x1b[33m'
ANSI_COLOR_BLUE = '\x1b[34m'
ANSI_COLOR_MAGENTA = '\x1b[35m'
ANSI_COLOR_BLACK = '\x1b[30m'
ANSI_COLOR_RESET = '\x1b[0m'


colours = [ANSI_COLOR_BLUE, ANSI_COLOR_GREEN, ANSI_COLOR_YELLOW, ANSI_COLOR_RED, ANSI_COLOR_MAGENTA]

BAR_WIDTH = 80

min_pressure = 1 << 32
max_pressure = 0

min_temperature = 1 << 32
max_temperature = 0

min_altitude = 1 << 32
max_altitude = 0


if len(sys.argv) > 1:
    QNH = float(sys.argv[1])

if QNH == 1013.25:
    print("QNH is set to the default of 1013.25. Altitude may not be accurate!")


def calculate_altitude(pressure, qnh=1013.25):
    return 44330.0 * (1.0 - pow(pressure / qnh, (1.0 / 5.255)))


device = ICP10125()

try:
    while True:
        pressure, temperature = device.measure(ULTRA_LOW_NOISE)
        altitude = calculate_altitude(pressure / 100.0, QNH)

        min_pressure = min(pressure - 100, min_pressure)
        max_pressure = max(pressure + 100, max_pressure)
        min_temperature = min(temperature - 5, min_temperature)
        max_temperature = max(temperature + 5, max_temperature)
        min_altitude = min(altitude - 1, min_altitude)
        max_altitude = max(altitude + 1, max_altitude)

        if max_pressure - min_pressure == 0 or max_temperature - min_temperature == 0 or max_altitude - min_altitude == 0:
            continue

        t_scale = min((temperature - min_temperature) / (max_temperature - min_temperature), 1.0)
        p_scale = min((pressure - min_pressure) / (max_pressure - min_pressure), 1.0)
        a_scale = min((altitude - min_altitude) / (max_altitude - min_altitude), 1.0)
        t_colour = colours[int((len(colours) - 1) * t_scale)]
        p_colour = colours[int((len(colours) - 1) * p_scale)]
        a_colour = colours[int((len(colours) - 1) * a_scale)]
        t_bar = BAR_CHAR * int(BAR_WIDTH * t_scale)
        p_bar = BAR_CHAR * int(BAR_WIDTH * p_scale)
        a_bar = BAR_CHAR * int(BAR_WIDTH * a_scale)

        t_bar += ANSI_COLOR_BLACK + (BAR_CHAR * (BAR_WIDTH - len(t_bar)))
        p_bar += ANSI_COLOR_BLACK + (BAR_CHAR * (BAR_WIDTH - len(p_bar)))
        a_bar += ANSI_COLOR_BLACK + (BAR_CHAR * (BAR_WIDTH - len(a_bar)))

        t_bar = t_colour + t_bar + ANSI_COLOR_RESET
        p_bar = p_colour + p_bar + ANSI_COLOR_RESET
        a_bar = a_colour + a_bar + ANSI_COLOR_RESET

        t_reading = "{:.4f}c".format(temperature).ljust(BAR_WIDTH + 14)
        p_reading = "{:.4f}hPa".format(pressure / 100).ljust(BAR_WIDTH + 14)
        a_reading = "{:.2f}m".format(altitude).ljust(BAR_WIDTH + 14)

        sys.stdout.write('\x1b[0;1H')
        sys.stdout.write(u"""{title}
{blank}
Temperature:  {t_bar}
{t_reading}
Pressure:     {p_bar}
{p_reading}
Altitude:     {a_bar}
{a_reading}
{blank}
""".format(
            title="ICP10125 Sensor".ljust(BAR_WIDTH + 14, " "),
            t_bar=t_bar,
            p_bar=p_bar,
            a_bar=a_bar,
            t_reading=t_reading,
            p_reading=p_reading,
            a_reading=a_reading,
            blank=" " * (BAR_WIDTH + 14)
        ))
        sys.stdout.flush()

except KeyboardInterrupt:
    pass
