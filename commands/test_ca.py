from data_sources.cycle_analyst import ca_record_from_software_serial, get_ca_software_serial
from data_sources.software_serial import close_software_serial
import time

def test_ca_telemetry():
    serial = get_ca_software_serial()
    if serial is None:
        print('Software serial not initialized')
        return
    try:
        while True:
            res = ca_record_from_software_serial(serial)
            if res is not None:
                print(res)
            time.sleep(0.3)
    except Exception as e:
        print(e)
    finally:
        close_software_serial(serial)
