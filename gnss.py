import serial
from pynmeagps import NMEAReader
from pynmeagps.exceptions import NMEAParseError
from datetime import datetime
import os
import logging

from utils import GNSSRecord

GNSS_SERIAL_INTERFACE = os.environ.get('GNSS_SERIAL', '/dev/ttyS0')
GNSS_BAUD_RATE = 115200
GNSS_SERIAL_TIMEOUT = 1

GNSS_SERIAL = serial.Serial(
    port=GNSS_SERIAL_INTERFACE,
    baudrate=GNSS_BAUD_RATE,
    timeout=1
)

GLL = 'GLL' # Geographic Position - Latitude/Longitude
GSV = 'GSV' # GNSS Satellites in View
GSA = 'GSA' # GNSS DOP and Active Satellites
GGA = 'GGA' # Global positioning system fix data
RMC = 'RMC' # Recommended Minimum data
VTG = 'VTG' # Course over ground and Groundspeed

def gnss_from_serial(ser: serial.Serial) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        line = ser.readline()
        result = NMEAReader.parse(line)
        lon = None
        lat = None
        alt = None
        spd = None
        if result is None:
            return
        if result.msgID == GGA:
            lon = result.lon
            lat = result.lat
            alt = result.alt
        elif result.msgID == RMC:
            lon = result.lon
            lat = result.lat
            spd = result.spd
        elif result.msgID == GLL:
            lon = result.lon
            lat = result.lat
        elif result.msgID in [GSA, GSV]:
            return None
        elif result.msgID == VTG:
            return None
        else:
            logger.error(f'Unknown message {result.msgID}')
        record = GNSSRecord(
            timestamp=datetime.timestamp(datetime.now()),
            longitude=lon,
            latitude=lat,
            altitude=alt,
            speed=spd
        )
        return record
    except serial.SerialException as e:
        logger.error('GNSS Serial error: {}'.format(e))
        return None
    except NMEAParseError as e:
        logger.error('NMEA Parse error: {}'.format(e))

for x in range(2000):
    res = gnss_from_serial(GNSS_SERIAL)
    if res is not None:
        print(res)
