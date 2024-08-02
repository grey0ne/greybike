import serial
import os
import logging
from datetime import datetime
from serial.serialutil import SerialException
from utils import CATelemetryRecord, get_random_value
from constants import SERIAL_TIMEOUT, SERIAL_BAUD_RATE

CA_INTERFACE = os.environ.get('CA_SERIAL')
CA_LINE_VALUES_COUNT = 14


def parse_telemetry_line(line: bytes) -> CATelemetryRecord | None:
    logger = logging.getLogger('greybike')
    try:
        values = line.decode("utf-8").replace('\r\n', '').split('\t')
    except Exception as e:
        logger.error(f'Error decoding serial line: {e}')
        return None
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


def ca_record_from_serial(ser: serial.Serial) -> CATelemetryRecord | None:
    line = ser.readline()
    return parse_telemetry_line(line)


def ca_record_from_random(previous: CATelemetryRecord | None) -> CATelemetryRecord:
    return CATelemetryRecord(
        timestamp=datetime.timestamp(datetime.now()),
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

def get_ca_serial_interface() -> serial.Serial | None:
    logger = logging.getLogger('greybike')
    try:
        ser = serial.Serial(CA_INTERFACE, SERIAL_BAUD_RATE, timeout=SERIAL_TIMEOUT)
        logger.info(f'Using serial interface {CA_INTERFACE}')
        return ser
    except SerialException:
        logger.error(f'Could not open serial interface {CA_INTERFACE}')
