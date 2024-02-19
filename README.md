# ICP10125 Barometric Pressure & Temperature Sensor

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/icp10125-python/test.yml?branch=main)](https://github.com/pimoroni/icp10125-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/icp10125-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/icp10125-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/icp10125.svg)](https://pypi.python.org/pypi/icp10125)
[![Python Versions](https://img.shields.io/pypi/pyversions/icp10125.svg)](https://pypi.python.org/pypi/icp10125)

# Pre-requisites

You must enable:

* i2c: `sudo raspi-config nonint do_i2c 0`

You can optionally run `sudo raspi-config` or the graphical Raspberry Pi Configuration UI to enable interfaces.

# Installing

Stable library from PyPi:

* Just run `python3 -m pip install icp10125`

In some cases you may need to use `sudo` or install pip with: `sudo apt install python3-pip`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/icp10125-python`
* `cd icp10125-python`
* `./install.sh --unstable`

