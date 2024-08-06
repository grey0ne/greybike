from datetime import datetime
from pathlib import Path
from typing import Any
from dataclasses import asdict
import json
import os
import psutil
import logging
import logging.config

from aiohttp import web

from telemetry import ca_record_from_serial, ca_record_from_random, get_ca_serial_interface
from ads import electric_record_from_ads, get_ads_interface, get_i2c_interface
from constants import (
    TELEMETRY_LOG_DIRECTORY, LOGGING_CONFIG, DEV_MODE,
    CA_TELEMETRY_READ_INTERVAL, CA_TELEMETRY_LOG_INTERVAL, CA_TELEMETRY_SEND_INTERVAL,
    ELECTRIC_RECORD_READ_INTERVAL,
    GNSS_READ_INTERVAL, FAVICON_DIRECTORY, JS_DIRECTORY,
    SYSTEM_PARAMS_READ_INTERVAL, MANIFEST, APP_LOG_DIRECTORY,
    PING_INTERVAL
)
from utils import AppState, check_running_on_pi, CATelemetryRecord, get_last_record, MessageType
from tasks import create_periodic_task
from telemetry_logs import write_to_log, reset_log
from dash_page import DASH_PAGE_HTML
from logs_page import render_logs_page
from wifi import ping_router
from gnss import gnss_from_serial, gnss_from_random, get_gnss_serial


if check_running_on_pi():
    from gpiozero import CPUTemperature # type: ignore
else:
    CPUTemperature = None

FAVICON_FILES = ['favicon-16.png', 'favicon-32.png', 'favicon-96.png', 'touch-icon-76.png']
PORT = int(os.environ.get('PORT', 8080))
TELEMETRY_TASK = 'telemetry_task'
WS_TIMEOUT = 0.1 # in seconds

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('greybike')

async def http_handler(request: web.Request):
    return web.Response(text=DASH_PAGE_HTML, content_type='text/html')

async def manifest_handler(request: web.Request):
    return web.Response(text=MANIFEST, content_type='application/json')

async def reset_log_handler(request: web.Request):
    reset_log(request.app['state'])
    return web.Response(text='Log file reset')

def get_file_serve_handler(file_path: str):
    async def file_serve_handler(request: web.Request):
        response = web.FileResponse(file_path)
        response.headers.setdefault('Cache-Control', 'max-age=3600')
        return response
    return file_serve_handler

async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse(timeout=WS_TIMEOUT)
    await ws.prepare(request)
    state: AppState = request.app['state']
    state.websockets.append(ws)
    try:
        async for msg in ws:
            logger.debug(f'Websocket message {msg}')
    finally:
        state.websockets.remove(ws)
    return ws

async def send_ws_message(state: AppState, message_type: MessageType, data: dict[str, Any]):
    message = {
        'type': message_type,
        'data': data
    }
    message_str = json.dumps(message)
    for ws in state.websockets:
        await ws.send_str(message_str)


async def read_system_params(state: AppState):
    data_dict: dict[str, float | str | None] = {}
    if CPUTemperature is not None:
        data_dict['cpu_temperature'] = CPUTemperature().temperature
    else:
        data_dict['cpu_temperature'] = None
    data_dict['memory_usage'] = psutil.virtual_memory().percent
    data_dict['cpu_usage'] = psutil.cpu_percent()
    if state.log_file is not None:
        data_dict['log_file'] = state.log_file.name.split('/')[-1]
    if state.log_start_time is not None:
        data_dict['log_duration'] = (datetime.now() - state.log_start_time).total_seconds()
    await send_ws_message(state, MessageType.SYSTEM, data_dict)


def read_ca_telemetry_record(state: AppState) -> CATelemetryRecord | None:
    if DEV_MODE:
        last_record = get_last_record(state.ca_telemetry_records)
        return ca_record_from_random(last_record)
    else:
        if state.ca_serial is not None:
            return ca_record_from_serial(state.ca_serial)


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
        await send_ws_message(state, MessageType.TELEMETRY, asdict(last_record))

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
    if state.ads is not None:
        state.electric_records.append(electric_record_from_ads(state.ads))

async def electric_telemetry_send_task(state: AppState):
    last_record = get_last_record(state.electric_records, ELECTRIC_RECORD_READ_INTERVAL)
    if last_record is not None:
        await send_ws_message(state, MessageType.ELECTRIC, asdict(last_record))

async def on_shutdown(app: web.Application):
    state: AppState = app['state']
    if state.ca_serial is not None:
        state.ca_serial.close()
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
    create_periodic_task(gnss_read_task, state, name="GNSS", interval=GNSS_READ_INTERVAL)
    create_periodic_task(ca_telemetry_read_task, state, name="Cycle Analyst Telemetry", interval=CA_TELEMETRY_READ_INTERVAL)
    create_periodic_task(ca_telemetry_log_task, state, name="Cycle Analyst Log", interval=CA_TELEMETRY_LOG_INTERVAL)
    create_periodic_task(ca_telemetry_websocket_task, state, name="Send CA Telemetry", interval=CA_TELEMETRY_SEND_INTERVAL)
    create_periodic_task(electric_telemetry_read_task, state, name="Electric Telemetry Read", interval=ELECTRIC_RECORD_READ_INTERVAL)
    create_periodic_task(read_system_params, state, name="System Params", interval=SYSTEM_PARAMS_READ_INTERVAL)


async def cleanup_background_tasks(app: web.Application):
    state: AppState = app['state']
    for task_data in state.tasks:
        logger.info(f'Cancelling task {task_data.name}')
        task_data.task.cancel()


async def log_list_handler(request: web.Request):
    state: AppState = request.app['state']
    return web.Response(text=render_logs_page(state.log_files), content_type='text/html')


def get_all_log_files():
    return os.listdir(TELEMETRY_LOG_DIRECTORY)

def setup_routes(app: web.Application):
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', websocket_handler),
        web.get('/manifest.json', manifest_handler),
        web.get('/chart.js', get_file_serve_handler(f'{JS_DIRECTORY}/chart.js')),
        web.get('/logs', log_list_handler),
        web.post('/reset_log', reset_log_handler)
    ])
    for icon_file in FAVICON_FILES:
        app.add_routes([
            web.get(f'/{icon_file}', get_file_serve_handler(f'{FAVICON_DIRECTORY}/{icon_file}'))
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
        state.ca_serial = get_ca_serial_interface()
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
    web.run_app(app=app, host='0.0.0.0', port=PORT) # type: ignore


if __name__ == "__main__":
    if DEV_MODE:
        logger.info('Running in development mode. CA Telemetry will be generated randomly.')
    start_server()
