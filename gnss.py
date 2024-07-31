import serial
from pynmeagps import NMEAReader
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

def gnss_from_serial(ser: serial.Serial) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        line = ser.readline()
        result = NMEAReader.parse(line)
        print(result)
    except serial.SerialException as e:
        logger.error('Device error: {}'.format(e))
        return None

for x in range(100):
    gnss_from_serial(GNSS_SERIAL)
