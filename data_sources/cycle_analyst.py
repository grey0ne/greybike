import serial
import logging
from datetime import datetime
from serial.serialutil import SerialException
from utils import get_random_value
from data_types import CATelemetryRecord, SoftwareSerial
from constants import SERIAL_TIMEOUT, CA_SERIAL_BAUD_RATE, CA_HARDWARE_SERIAL, CA_SOFTWARE_SERIAL_PIN
from data_sources.software_serial import readlines_from_software_serial, init_software_serial

CA_LINE_VALUES_COUNT = 14

def parse_telemetry_line(line: str) -> CATelemetryRecord | None:
    logger = logging.getLogger('greybike')
    values = line.replace('\r\n', '').split('\t')
    if len(values) != CA_LINE_VALUES_COUNT:
        logger.error(f'Incorrect number of values in serial line: {len(values)} expected {CA_LINE_VALUES_COUNT}')
        return None
    flags = values[13]
    return CATelemetryRecord(
        timestamp=datetime.timestamp(datetime.now()),
        amper_hours=float(values[0]),
        voltage=float(values[1]),
        current=float(values[2]),
        speed=float(values[3]),
        trip_distance=float(values[4]),
        motor_temp=float(values[5]),
        pedal_rpm=float(values[6]),
        human_watts=float(values[7]),
        human_torque=float(values[8]),
        throttle_input=float(values[9]),
        throttle_output=float(values[10]),
        aux_a=float(values[11]),
        aux_d=float(values[12]),
        flags=flags,
        mode=int(flags[0]),
        is_brake_pressed='B' in flags
    )


def ca_record_from_hardware_serial(ser: serial.Serial) -> CATelemetryRecord | None:
    logger = logging.getLogger('greybike')
    line = ser.readline()
    try:
        line = line.decode("utf-8")
    except Exception as e:
        logger.error(f'Error decoding serial line: {e}')
        return None
    return parse_telemetry_line(line)

def ca_record_from_software_serial(ser: SoftwareSerial) -> CATelemetryRecord | None:
    """
        Returns the latest sucessfully parsed telemetry record from the Cycle Analyst V3
    """
    lines = readlines_from_software_serial(ser)
    parsed_line = None
    for line in lines:
        result = parse_telemetry_line(line)
        if result is not None:
            parsed_line = result
    return parsed_line

def ca_record_from_random(previous: CATelemetryRecord | None) -> CATelemetryRecord:
    return CATelemetryRecord(
        amper_hours=get_random_value(0, 10, 0.01, previous and previous.amper_hours),
        voltage=get_random_value(35, 55, 0.1, previous and previous.voltage),
        current=get_random_value(0, 25, 1, previous and previous.current),
        speed=get_random_value(0, 50, 1, previous and previous.speed),
        trip_distance=get_random_value(0, 100, 0.1, previous and previous.trip_distance),
        motor_temp=get_random_value(20, 80, 0.1, previous and previous.motor_temp),
        pedal_rpm=get_random_value(0, 200, 10, previous and previous.pedal_rpm),
        human_watts=get_random_value(0, 500, 1, previous and previous.human_watts),
        human_torque=get_random_value(0, 50, 0.1, previous and previous.human_torque),
        throttle_input=get_random_value(0, 100, 0.1, previous and previous.throttle_input),
        throttle_output=get_random_value(0, 100, 0.1, previous and previous.throttle_output),
        aux_a=0,
        aux_d=0,
        flags='',
        mode=1,
        is_brake_pressed=False
    )

def get_ca_hardware_serial() -> serial.Serial | None:
    logger = logging.getLogger('greybike')
    if CA_HARDWARE_SERIAL is None:
        logger.error('CA_HARDWARE_SERIAL is not set using software serial')
        return None
    try:
        ser = serial.Serial(CA_HARDWARE_SERIAL, CA_SERIAL_BAUD_RATE, timeout=SERIAL_TIMEOUT)
        logger.info(f'Using hardware serial interface for CA {CA_HARDWARE_SERIAL}')
        return ser
    except SerialException:
        logger.error(f'Could not open serial interface {CA_HARDWARE_SERIAL}')


def get_ca_software_serial() -> SoftwareSerial | None:
    logger = logging.getLogger('greybike')
    if CA_HARDWARE_SERIAL is not None:
        # If hardware serial is set, software serial is not used
        return None
    try:
        ser = init_software_serial(CA_SOFTWARE_SERIAL_PIN, CA_SERIAL_BAUD_RATE)
        logger.info(f'Using software serial interface on GPIO {CA_SOFTWARE_SERIAL_PIN}')
        return ser
    except Exception as e:
        logger.error(f'Could not open software serial interface on GPIO {CA_SOFTWARE_SERIAL_PIN}: {e}')