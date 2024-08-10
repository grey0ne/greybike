from data_sources.gnss import gnss_from_serial, get_gnss_serial

GNSS_SERIAL = get_gnss_serial()

for x in range(2000):
    res = gnss_from_serial(GNSS_SERIAL)
    if res is not None:
        print(res)