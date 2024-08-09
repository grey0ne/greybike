import time
from ads import electric_record_from_ads, get_ads_interface, get_i2c_interface

def rd(value: float):
    return round(value, 4)

def test_ads_sensor():
    i2c = get_i2c_interface()
    if i2c is None:
        print('I2C not initialized')
        return
    ads = get_ads_interface(i2c)

    while True:
        if ads is not None:
            record = electric_record_from_ads(ads)
            power = record.current * record.voltage
            print(f"Voltage: {rd(record.voltage)} Amps: {rd(record.current)} Watts: {rd(power)}")
        time.sleep(0.2)

test_ads_sensor()
