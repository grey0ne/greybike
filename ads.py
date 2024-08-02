import board # type: ignore Library does not have proper typing
import busio # type: ignore Library does not have proper typing
import adafruit_ads1x15.ads1115 as ADS
from datetime import datetime
from adafruit_ads1x15.analog_in import AnalogIn
from utils import ElectricalRecord, get_random_value


BASE_VOLTAGE = 2.515 # ACS712 20A sensor has 2.5V output when no current is flowing
AMP_CONVERSION_CF = 9.93 # ACS712 20A coefficient should be exactly 10 (100mV/A) but after calibration this value works better

VOLTAGE_DIVIDER_CF = 21 # 200kOhm / 10kOhm voltage divider


def electric_record_from_ads(ads: ADS.ADS1115) -> ElectricalRecord:
    current_channel = AnalogIn(ads, ADS.P0) # ACS712 20A sensor connected to A0. Measures current flowing to the bike's electronics
    voltage_channel = AnalogIn(ads, ADS.P1) # Voltage divider connected to A1. Measures battery voltage
    amps = (BASE_VOLTAGE - current_channel.voltage) * AMP_CONVERSION_CF
    battery_voltage = voltage_channel.voltage * VOLTAGE_DIVIDER_CF
    print(f"A1 Value: {voltage_channel.voltage} Voltage: {battery_voltage} Amps: {amps} Watts: {amps * battery_voltage}")
    return ElectricalRecord(
        timestamp=datetime.timestamp(datetime.now()),
        current=amps,
        voltage=battery_voltage
    )

def electric_record_from_random(previous: ElectricalRecord | None) -> ElectricalRecord:
    return ElectricalRecord(
        timestamp=datetime.timestamp(datetime.now()),
        current=get_random_value(0, 5, 0.05, previous and previous.current),
        voltage=get_random_value(38, 55, 0.1, previous and previous.voltage)
    )

def get_ads_interface() -> ADS.ADS1115 | None:
    i2c = busio.I2C(board.SCL, board.SDA) # type: ignore
    ads = ADS.ADS1115(i2c)
    ads.gain = 1
    return ads
