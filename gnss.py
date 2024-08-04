import serial
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

KNOTS_TO_KMH = 1.852

GLL = ['GPGLL', 'GNGLL'] # Geographic Position - Latitude/Longitude
GSV = ['GPGSV', 'GLGSV', 'GBGSV', 'GAGSV', 'GQGSV'] # GNSS Satellites in View
GSA = ['GNGSA'] # GNSS DOP and Active Satellites
GGA = ['GPGGA', 'GNGGA'] # Global positioning system fix data
RMC = ['GNRMC','GPRMC'] # Recommended Minimum data
VTG = ['GNVTG'] # Course over ground and Groundspeed


def parse_GGA(values: list[str]) -> GNSSRecord:
    try:
        return GNSSRecord(
            latitude=float(values[2]),
            longitude=float(values[4]),
            sat_num=int(values[7]),
            hdop=float(values[8]),
            altitude=float(values[9])
        )
    except ValueError:
        print(values)

def parse_RMC(values: list[str]) -> GNSSRecord:
    try:
        return GNSSRecord(
            latitude=float(values[3]),
            longitude=float(values[5]),
            speed=float(values[7]) * KNOTS_TO_KMH
        )
    except ValueError:
        print(values)

def parse_GLL(values: list[str]) -> GNSSRecord:
    try:
        return GNSSRecord(
            latitude=float(values[1]),
            longitude=float(values[3]),
        )
    except ValueError:
        print(values)

def process_nmea_line(line: bytes) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    nmea_values = line.decode("utf-8").replace('\r\n', '').split(',')
    msgID = nmea_values[0].replace('$', '') 
    if msgID in GGA:
        return parse_GGA(nmea_values)
    if msgID in RMC:
        return parse_RMC(nmea_values)
    if msgID in GLL:
        return parse_GLL(nmea_values)
    if msgID in GSA + GSV + VTG:
        return None
    logger.error(f'Unknown message {msgID}')
    return None

def gnss_from_serial(ser: serial.Serial) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        line = ser.readline()
        return process_nmea_line(line)
    except serial.SerialException as e:
        logger.error('GNSS Serial error: {}'.format(e))
        return None

for x in range(2000):
    res = gnss_from_serial(GNSS_SERIAL)
    if res is not None:
        print(res)
