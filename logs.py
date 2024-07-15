from constants import LOG_VERSION, TELEMETRY_LOG_DIRECTORY, LOG_RECORD_COUNT_LIMIT
from datetime import datetime
from utils import AppState
from telemetry import TelemetryRecord
import os
import logging

logger = logging.getLogger('greybike')

LOG_HEADER_TEMPLATE = """
GREYBIKE LOG
VERSION v{version}
FIELDS {fields}
"""
LOG_FIELDS = [
    'timestamp', 'speed', 'voltage', 'current', 'trip_distance', 'amper_hours', 'motor_temp',
    'pedal_rpm', 'human_torque', 'human_watts', 'throttle_input', 'throttle_output',
    'mode'
]

def write_to_log(state: AppState, telemetry: TelemetryRecord | None):
    if telemetry is not None:
        if state.log_record_count >= LOG_RECORD_COUNT_LIMIT:
            reset_log(state)
        data = telemetry.__dict__
        data['timestamp'] = "%.2f" % datetime.timestamp(datetime.now())
        log_record = ','.join(str(data[field]) for field in LOG_FIELDS)
        if state.log_file is None:
            raise ValueError('Log file not open')
        state.log_file.write(f'{log_record}\n')


def reset_log(state: AppState):
    if state.log_file is not None:
        logger.info(f'Closing log file {state.log_file.name}')
        state.log_file.close()
    state.log_record_count = 0
    state.log_start_time = datetime.now()
    log_file_name = f'{state.log_start_time.isoformat()}.log'
    log_file_path = os.path.join(TELEMETRY_LOG_DIRECTORY, log_file_name)
    logger.info(f'Logging telemetry to {log_file_path}')
    state.log_file = open(log_file_path, 'w+')
    state.log_files.append(log_file_name)
    log_header = LOG_HEADER_TEMPLATE.format(
        version=LOG_VERSION, fields=','.join(LOG_FIELDS)
    )
    state.log_file.write(log_header)






