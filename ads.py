import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
chan = AnalogIn(ads, ADS.P0)

BASE_VOLTAGE = 2.515
AMP_CONVERSION_CF = 9.93
BATTERY_VOLTAGE = 52.6


while True:
    amps = (BASE_VOLTAGE - chan.voltage) * AMP_CONVERSION_CF
    print(f"Voltage: {chan.voltage} Amps: {amps} Watts: {amps * BATTERY_VOLTAGE}")
    time.sleep(0.5)
