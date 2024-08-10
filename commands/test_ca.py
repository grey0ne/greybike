from data_sources.cycle_analyst import ca_record_from_software_serial, get_ca_software_serial

def test_ca_telemetry():
    serial = get_ca_software_serial()
    if serial is None:
        print('Software serial not initialized')
        return
    while True:
        res = ca_record_from_software_serial(serial)
        if res is not None:
            print(res)