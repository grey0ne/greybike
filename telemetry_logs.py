from constants import LOG_VERSION, TELEMETRY_LOG_DIRECTORY, LOG_RECORD_COUNT_LIMIT
from datetime import datetime
from data_types import AppState, CATelemetryRecord
from dataclasses import dataclass, fields, asdict
from typing import Generator
import os
import logging

LOG_HEADER_TEMPLATE = """GREYBIKE LOG
VERSION v{version}
FIELDS {fields}
"""


@dataclass
class LogRecord:
    timestamp: float
    speed: float | None = None
    voltage: float | None = None
    current: float | None = None
    trip_distance: float | None = None
    amper_hours: float | None = None
    motor_temp: float | None = None
    pedal_rpm: float | None = None
    human_torque: float | None = None
    human_watts: float | None = None
    throttle_input: float | None = None
    throttle_output: float | None = None
    mode: float | None = None

class AggregatedLogData:
    max_speed: float = 0
    max_regen_watts: float = 0
    max_motor_watts: float = 0
    max_human_watts: float = 0
    total_human_watt_hours: float = 0
    total_regen_watt_hours: float = 0
    total_motor_watt_hours: float = 0
    total_distance: float = 0
    total_records: int = 0

def get_log_fields():
    return [field.name for field in fields(LogRecord)]


def write_to_log(state: AppState, telemetry: CATelemetryRecord | None):
    if telemetry is not None:
        if state.log_record_count >= LOG_RECORD_COUNT_LIMIT:
            reset_log(state)
        data = asdict(telemetry)
        data['timestamp'] = "%.2f" % telemetry.timestamp
        log_record = ','.join(str(data[field]) for field in get_log_fields())
        if state.log_file is None:
            raise ValueError('Log file not open')
        state.log_file.write(f'{log_record}\n')


def reset_log(state: AppState):
    logger = logging.getLogger('greybike')
    if state.log_file is not None:
        logger.info(f'Closing log file {state.log_file.name}')
        state.log_file.close()
        state.log_file = None
    state.log_record_count = 0
    state.log_start_time = datetime.now()
    log_file_name = f'{state.log_start_time.isoformat()}.log'
    log_file_path = os.path.join(TELEMETRY_LOG_DIRECTORY, log_file_name)
    logger.info(f'Logging telemetry to {log_file_path}')
    log_file = open(log_file_path, 'w+')
    log_header = LOG_HEADER_TEMPLATE.format(
        version=LOG_VERSION, fields=','.join(get_log_fields())
    )
    log_file.write(log_header)
    state.log_file = log_file
    state.log_files.append(log_file_name)


def get_fields_from_log_header(header: str) -> list[str]:
    return header.split('FIELDS ')[1].split(',')


def read_log_file(file_name: str) -> Generator[LogRecord, None, None]:
    logger = logging.getLogger('greybike')
    with open(os.path.join(TELEMETRY_LOG_DIRECTORY, file_name)) as log_file:
        header = log_file.readline()
        if not header.startswith('GREYBIKE LOG'):
            raise ValueError('Invalid log file')
        version = log_file.readline().split('v')[1].strip()
        logger.debug(f'Log file version {version}')
        fields_line = log_file.readline()
        fields = get_fields_from_log_header(fields_line)
        log_obj_fields = set(get_log_fields())
        while True:
            line = log_file.readline()
            if not line:
                break
            values = line.split(',')
            data = {field: float(values[i]) for i, field in enumerate(fields)}

            yield LogRecord(**{k: v for k, v in data.items() if k in log_obj_fields})


def calculate_log_agregates(file_name: str, start: float, end: float):
    result = AggregatedLogData()
    prev_timestamp = None
    start_distance = None
    end_distance = None
    for record in read_log_file(file_name):
        if record.timestamp >= start and record.timestamp <= end:
            result.total_records += 1
            duration = record.timestamp - prev_timestamp if prev_timestamp is not None else 0.1
            if duration > 1:
                duration = 0.1
            if record.current and record.voltage:
                if record.current < 0:
                    regen_watts = -(record.voltage * record.current)
                    result.max_regen_watts = max(result.max_regen_watts, regen_watts)
                    result.total_regen_watt_hours += (regen_watts / 3600) * duration
                else:
                    motor_watts = record.voltage * record.current
                    result.max_motor_watts = max(result.max_motor_watts, motor_watts)
                    result.total_motor_watt_hours += (motor_watts / 3600) * duration
            if start_distance is None:
                start_distance = record.trip_distance
            end_distance = record.trip_distance
            prev_timestamp = record.timestamp
            if record.speed is not None:
                result.max_speed = max(result.max_speed, record.speed)
            if record.human_watts is not None:
                result.max_human_watts = max(result.max_human_watts, record.human_watts)
                result.total_human_watt_hours += (record.human_watts / 3600) * duration
    result.total_distance = end_distance - start_distance if start_distance is not None and end_distance is not None else 0
    return result