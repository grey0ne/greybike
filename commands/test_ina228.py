import time
import board
from data_sources.ina228 import INA228

def test_ina228():
    i2c = board.I2C()
    ina228 = INA228(i2c)
    while True:
        print("Current: %.2f Voltage: %.2f Power:%.2f Temp %.2f" % (ina228.current, ina228.voltage, ina228.power, ina228.temp))
        time.sleep(1)
