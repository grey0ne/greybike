import serial
import logging

from utils import get_random_value
from data_types import GNSSRecord
from constants import GNSS_BAUD_RATE, GNSS_SERIAL_INTERFACE

GNSS_SERIAL_TIMEOUT = 1

KNOTS_TO_KMH = 1.852

GLL = ['GPGLL', 'GNGLL'] # Geographic Position - Latitude/Longitude
GSV = ['GPGSV', 'GLGSV', 'GBGSV', 'GAGSV', 'GQGSV'] # GNSS Satellites in View
GSA = ['GNGSA'] # GNSS DOP and Active Satellites
GGA = ['GPGGA', 'GNGGA'] # Global positioning system fix data
RMC = ['GNRMC','GPRMC', 'GGNRMC'] # Recommended Minimum data
VTG = ['GNVTG'] # Course over ground and Groundspeed

def get_gnss_serial() -> serial.Serial:
    return serial.Serial(
        port=GNSS_SERIAL_INTERFACE,
        baudrate=GNSS_BAUD_RATE,
        timeout=GNSS_SERIAL_TIMEOUT
    )

def parse_GGA(values: list[str]) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        return GNSSRecord(
            latitude=float(values[2]),
            longitude=float(values[4]),
            sat_num=int(values[7]),
            hdop=float(values[8]),
            altitude=float(values[9])
        )
    except (ValueError, IndexError):
        logger.debug(f'Error parsing GGA: {values}') # This happens when GPS signal is absent

def parse_RMC(values: list[str]) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        return GNSSRecord(
            latitude=float(values[3]),
            longitude=float(values[5]),
            speed=float(values[7]) * KNOTS_TO_KMH
        )
    except (ValueError, IndexError):
        logger.debug(f'Error parsing RMC: {values}') # This happens when GPS signal is absent

def parse_GLL(values: list[str]) -> GNSSRecord | None:
    logger = logging.getLogger('greybike')
    try:
        return GNSSRecord(
            latitude=float(values[1]),
            longitude=float(values[3]),
        )
    except (ValueError, IndexError):
        logger.debug(f'Error parsing GGA: {values}') # This happens when GPS signal is absent

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


def gnss_from_random(previous: GNSSRecord | None ) -> GNSSRecord | None:
    return GNSSRecord(
        latitude=get_random_value(99, 100, 0.001, previous and previous.latitude),
        longitude=get_random_value(99, 100, 0.001, previous and previous.longitude),
        speed=get_random_value(10, 40, 0.5, previous and previous.speed),
        altitude=get_random_value(800, 1000, 1, previous and previous.altitude),
        sat_num=int(get_random_value(0, 20, 1, previous and previous.sat_num)),
    )
