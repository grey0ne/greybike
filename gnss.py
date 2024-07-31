import serial
from pynmeagps import NMEAReader
from pynmeagps.exceptions import NMEAParseError
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

def gnss_from_serial(ser: serial.Serial) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        line = ser.readline()
        result = NMEAReader.parse(line)
        print(result)
        if result.msgID == GLL:
            print(result.lat, result.lon)
    except serial.SerialException as e:
        logger.error('GNSS Serial error: {}'.format(e))
        return None
    except NMEAParseError as e:
        logger.error('NMEA Parse error: {}'.format(e))

for x in range(100):
    gnss_from_serial(GNSS_SERIAL)
