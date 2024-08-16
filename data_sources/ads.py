try:
    import board # type: ignore Library does not have proper typing
except:
    board = None
import busio # type: ignore Library does not have proper typing
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from data_types import ElectricalRecord
from utils import get_random_value
import logging
import math


AMP_CONVERSION_CF = 0.185 # ACS712 5A coefficient (185mv/A)

VOLTAGE_DIVIDER_CF = 21.7 # 200kOhm / 10kOhm voltage divider. And some further calubration
BASE_VOLTAGE = 2.4755

NOMINAL_TEMP = 25
THERMISTOR_CF = 3950
THERMISTOR_R = 10000 # 10kOm thermistor
RESISTOR = 10000 # 10kOm resistor

TEMP_CF = 273.15

def calculate_temp_from_voltage(thermistor_voltage: float, reference_voltage: float) -> float:
    vcf = thermistor_voltage / (reference_voltage * 2)
    thermistor_resistance = (vcf * RESISTOR) / (1 - vcf)
    temp = 1 / (math.log(thermistor_resistance/THERMISTOR_R) / THERMISTOR_CF + 1 / (NOMINAL_TEMP + TEMP_CF)) - TEMP_CF
    return temp

def sf(value: float) -> str:
    return "{:.4f}".format(value)

def debug_voltages(cur: float, vol: float, therm: float):
    print("Cur:", sf(cur), "V:", sf(vol), "Therm:", sf(therm))


def electric_record_from_ads(ads: ADS.ADS1115) -> ElectricalRecord:
    logger = logging.getLogger('greybike')
    current_channel = AnalogIn(ads, ADS.P0) # ACS712 20A sensor connected to A0. Measures current flowing to the bike's electronics
    thermistor_channel = AnalogIn(ads, ADS.P1) # 10K Thermistor with 10K resistor
    voltage_channel = AnalogIn(ads, ADS.P2, ADS.P3)
    #voltage_channel = AnalogIn(ads, ADS.P1) # Voltage divider connected to A1. Measures battery voltage
    #reference_voltage_channel = AnalogIn(ads, ADS.P2) # Voltage divider connected to A2. Should have halved main voltage
    try:
        temp = calculate_temp_from_voltage(thermistor_channel.voltage, BASE_VOLTAGE)
    except ValueError:
        logger.error('Error calculating temp')
        temp = None

    debug_voltages(current_channel.voltage, voltage_channel.voltage, thermistor_channel.voltage)

    amps = (BASE_VOLTAGE - current_channel.voltage) / AMP_CONVERSION_CF
    battery_voltage = voltage_channel.voltage * VOLTAGE_DIVIDER_CF
    return ElectricalRecord(
        temp=temp,
        current=amps,
        voltage=battery_voltage
    )

def electric_record_from_random(previous: ElectricalRecord | None) -> ElectricalRecord:
    return ElectricalRecord(
        current=get_random_value(0, 5, 0.05, previous and previous.current),
        voltage=get_random_value(38, 55, 0.5, previous and previous.voltage),
        temp=get_random_value(20, 50, 1, previous and previous.temp)
    )

def get_i2c_interface() -> busio.I2C | None:
    logger = logging.getLogger('greybike')
    if board is None:
        logger.error("Board not available")
        return None
    i2c = busio.I2C(board.SCL, board.SDA) # type: ignore
    return i2c

def get_ads_interface(i2c: busio.I2C) -> ADS.ADS1115 | None:
    ads = ADS.ADS1115(i2c)
    ads.gain = 1 # maximum measuring range of 6.144V
    return ads
