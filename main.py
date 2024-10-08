from pathlib import Path
from dataclasses import asdict
import os
import psutil
import logging
import logging.config

from aiohttp import web

from data_sources.cycle_analyst import (
    ca_record_from_hardware_serial, ca_record_from_random, get_ca_hardware_serial,
    ca_record_from_software_serial, get_ca_software_serial, 
)
from data_sources.software_serial import close_software_serial
from data_sources.ads import (
    electric_record_from_ads, get_ads_interface, get_i2c_interface, electric_record_from_random
)
from data_sources.gnss import gnss_from_serial, gnss_from_random, get_gnss_serial
from constants import (
    TELEMETRY_LOG_DIRECTORY, LOGGING_CONFIG, DEV_MODE, SPA_HTML_FILE,
    CA_TELEMETRY_READ_INTERVAL, CA_TELEMETRY_LOG_INTERVAL, CA_TELEMETRY_SEND_INTERVAL,
    ELECTRIC_RECORD_READ_INTERVAL, ELECTRIC_RECORD_SEND_INTERVAL,
    GNSS_READ_INTERVAL, GNSS_SEND_INTERVAL,
    SYSTEM_PARAMS_READ_INTERVAL, SYSTEM_PARAMS_SEND_INTERVAL, 
    APP_LOG_DIRECTORY, PING_INTERVAL, SERVER_PORT, MANIFEST_FILE
)
from utils import check_running_on_pi, get_last_record, send_ws_message
from handlers import (
    websocket_handler, spa_asset_handler, icons_handler,
    reset_log_handler, get_file_serve_handler
)
from data_types import AppState, CATelemetryRecord, MessageType, SystemTelemetryRecord
from tasks import create_periodic_task
from telemetry_logs import write_to_log, reset_log
from wifi import ping_router


if check_running_on_pi():
    from gpiozero import CPUTemperature # type: ignore
else:
    CPUTemperature = None


logging.config.dictConfig(LOGGING_CONFIG)


async def read_system_params(state: AppState):
    record = SystemTelemetryRecord(
        cpu_temp=None if CPUTemperature is None else CPUTemperature().temperature,
        cpu_usage=psutil.cpu_percent(),
        memory_usage=psutil.virtual_memory().percent
    )
    state.system_telemetry_records.append(record)


async def send_system_params(state: AppState):
    last_record = get_last_record(state.system_telemetry_records, SYSTEM_PARAMS_READ_INTERVAL)
    if last_record is not None:
        await send_ws_message(state, MessageType.SYSTEM, asdict(last_record))


def read_ca_telemetry_record(state: AppState) -> CATelemetryRecord | None:
    if DEV_MODE:
        last_record = get_last_record(state.ca_telemetry_records)
        return ca_record_from_random(last_record)
    else:
        if state.ca_hardware_serial is not None:
            return ca_record_from_hardware_serial(state.ca_hardware_serial)
        if state.ca_software_serial is not None:
            return ca_record_from_software_serial(state.ca_software_serial)



async def ca_telemetry_read_task(state: AppState):
    telemetry = read_ca_telemetry_record(state)
    if telemetry is not None:
        state.ca_telemetry_records.append(telemetry)


async def ca_telemetry_log_task(state: AppState):
    last_record = get_last_record(state.ca_telemetry_records, CA_TELEMETRY_READ_INTERVAL)
    if last_record is not None:
        state.log_record_count += 1
        write_to_log(state, last_record)


async def ca_telemetry_websocket_task(state: AppState):
    last_record = get_last_record(state.ca_telemetry_records, CA_TELEMETRY_READ_INTERVAL)
    if last_record is not None:
        await send_ws_message(state, MessageType.CA, asdict(last_record))


async def gnss_read_task(state: AppState):
    gnss_record = None
    if DEV_MODE:
        gnss_record = gnss_from_random(state.gnss_records[-1] if state.gnss_records else None)
    else:
        if state.gnss_serial is not None:
            gnss_record = gnss_from_serial(state.gnss_serial)
    if gnss_record is not None:
        state.gnss_records.append(gnss_record)


async def gnss_send_task(state: AppState):
    last_record = get_last_record(state.gnss_records, GNSS_READ_INTERVAL)
    if last_record is not None:
        await send_ws_message(state, MessageType.GNSS, asdict(last_record))


async def electric_telemetry_read_task(state: AppState):
    record = None
    if DEV_MODE:
        last_record = get_last_record(state.electric_records)
        record = electric_record_from_random(last_record)
    if state.ads is not None:
        record = electric_record_from_ads(state.ads)
    if record is not None:
        state.electric_records.append(record)


async def electric_telemetry_send_task(state: AppState):
    last_record = get_last_record(state.electric_records, ELECTRIC_RECORD_READ_INTERVAL)
    if last_record is not None:
        await send_ws_message(state, MessageType.ELECTRIC, asdict(last_record))


async def on_shutdown(app: web.Application):
    state: AppState = app['state']
    if state.ca_hardware_serial is not None:
        state.ca_hardware_serial.close()
    if state.ca_software_serial is not None:
        close_software_serial(state.ca_software_serial)
    if state.gnss_serial is not None:
        state.gnss_serial.close()
    if state.log_file is not None:
        state.log_file.close()
    for ws in state.websockets:
        await ws.close(code=999, message=b'Server shutdown')


async def start_background_tasks(app: web.Application):
    state: AppState = app['state']
    if not DEV_MODE:
        create_periodic_task(ping_router, state, name="Router Ping", interval=PING_INTERVAL)
    create_periodic_task(gnss_read_task, state, name="Read GNSS", interval=GNSS_READ_INTERVAL)
    create_periodic_task(gnss_send_task, state, name="Send GNSS", interval=GNSS_SEND_INTERVAL)
    create_periodic_task(ca_telemetry_read_task, state, name="Cycle Analyst Telemetry", interval=CA_TELEMETRY_READ_INTERVAL)
    create_periodic_task(ca_telemetry_log_task, state, name="Cycle Analyst Log", interval=CA_TELEMETRY_LOG_INTERVAL)
    create_periodic_task(ca_telemetry_websocket_task, state, name="Send CA Telemetry", interval=CA_TELEMETRY_SEND_INTERVAL)
    create_periodic_task(electric_telemetry_read_task, state, name="Read Electric Telemetry", interval=ELECTRIC_RECORD_READ_INTERVAL)
    create_periodic_task(electric_telemetry_send_task, state, name="Send Electric Telemetry", interval=ELECTRIC_RECORD_SEND_INTERVAL)
    create_periodic_task(read_system_params, state, name="Read System Params", interval=SYSTEM_PARAMS_READ_INTERVAL)
    create_periodic_task(send_system_params, state, name="Send System Params", interval=SYSTEM_PARAMS_SEND_INTERVAL)


async def cleanup_background_tasks(app: web.Application):
    logger = logging.getLogger('greybike')
    state: AppState = app['state']
    for task_data in state.tasks:
        logger.info(f'Cancelling task {task_data.name}')
        task_data.task.cancel()


def get_all_log_files():
    return os.listdir(TELEMETRY_LOG_DIRECTORY)

def setup_routes(app: web.Application):
    app.add_routes([
        web.get('/', get_file_serve_handler(SPA_HTML_FILE)),
        web.get('/ws', websocket_handler),
        web.get('/manifest.json', get_file_serve_handler(MANIFEST_FILE)),
        web.get('/assets/{file}', spa_asset_handler),
        web.get('/icons/{file}', icons_handler),
        web.post('/reset_log', reset_log_handler)
    ])

def create_dirs():
    Path(TELEMETRY_LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
    Path(APP_LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)

def init():
    create_dirs()
    app = web.Application()
    state = AppState(log_files=get_all_log_files())
    app['state'] = state
    if not DEV_MODE:
        state.ca_hardware_serial = get_ca_hardware_serial()
        state.ca_software_serial = get_ca_software_serial()
        state.i2c = get_i2c_interface()
        if state.i2c is not None:
            state.ads = get_ads_interface(state.i2c)
        state.gnss_serial = get_gnss_serial()
    reset_log(state)
    setup_routes(app)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(on_shutdown)
    return app


def start_server():
    app = init()
    web.run_app(app=app, host='0.0.0.0', port=SERVER_PORT) # type: ignore


if __name__ == "__main__":
    logger = logging.getLogger('greybike')
    if DEV_MODE:
        logger.info('Running in development mode. CA Telemetry will be generated randomly.')
    start_server()
