from data_sources.gnss import gnss_from_serial, get_gnss_serial

GNSS_SERIAL = get_gnss_serial()

def test_gnss_sensor():
    while True:
        res = gnss_from_serial(GNSS_SERIAL)
        if res is not None:
            print(res)