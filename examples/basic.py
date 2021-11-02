#!/usr/bin/env python3
import time
from icp10125 import ICP10125


device = ICP10125()
    
try:
    while True:
        pressure, temperature = device.measure()
        print(f"""Pressure: {pressure:.2f}hPa
Temperature: {temperature:.4f}c""")
        time.sleep(1.0)
except KeyboardInterrupt:
    pass


