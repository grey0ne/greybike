from datetime import datetime
from pathlib import Path
from typing import Any
from enum import StrEnum
import json
import os
import psutil
import logging
import logging.config
import asyncio

from aiohttp import web

from telemetry import ca_record_from_serial, ca_record_from_random, get_ca_serial_interface
from ads import electric_record_from_ads, get_ads_interface
from constants import (
    TELEMETRY_LOG_DIRECTORY,
    CA_TELEMETRY_READ_INTERVAL, CA_TELEMETRY_LOG_INTERVAL, CA_TELEMETRY_WEBSOCKET_INTERVAL,
    GNSS_READ_INTERVAL, FAVICON_DIRECTORY,
    SYSTEM_PARAMS_READ_INTERVAL, MANIFEST, APP_LOG_FILE, APP_LOG_DIRECTORY,
    PING_INTERVAL
)
from utils import AppState, check_running_on_pi, CATelemetryRecord, get_last_record
from tasks import create_periodic_task
from telemetry_logs import write_to_log, reset_log
from dash_page import DASH_PAGE_HTML
from logs_page import render_logs_page
from wifi import ping_router
from gnss import gnss_from_serial, gnss_from_random


if check_running_on_pi():
    from gpiozero import CPUTemperature # type: ignore
else:
    CPUTemperature = None

FAVICON_FILES = ['favicon-16.png', 'favicon-32.png', 'favicon-96.png', 'touch-icon-76.png']
PORT = int(os.environ.get('PORT', 8080))
DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'
TELEMETRY_TASK = 'telemetry_task'
WS_TIMEOUT = 0.1 # in seconds

class MessageType(StrEnum):
    SYSTEM = 'system'
    TELEMETRY = 'telemetry'
    EVENT = 'event'

LOGGING: dict[str, Any] = {
    'version': 1,
    'formatters': {
        'timestamp': {
            'format': '%(asctime)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': APP_LOG_FILE,
            'encoding': 'utf-8',
            'formatter': 'timestamp'
        }
    },
    'loggers': {}
}
if DEV_MODE:
    LOGGING['loggers']['greybike'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }
else:
    LOGGING['loggers']['greybike'] = {
        'level': 'INFO',
        'handlers': ['file']
    }

logging.config.dictConfig(LOGGING)
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
        return web.FileResponse(file_path)
    return file_serve_handler

async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse(timeout=WS_TIMEOUT)
    await ws.prepare(request)
    state: AppState = request.app['state']
    state.websockets.append(ws)
    try:
        async for msg in ws:
            logger.debug(f'Websocket message {msg}')
            await asyncio.sleep(1)
    finally:
        state.websockets.remove(ws)
    return ws

async def send_ws_message(app: web.Application, message_type: MessageType, data: dict[str, Any]):
    message = {
        'type': message_type,
        'data': data
    }
    message_str = json.dumps(message)
    state: AppState = app['state']
    for ws in state.websockets:
        await ws.send_str(message_str)


async def read_system_params(app: web.Application):
    data_dict: dict[str, float | str | None] = {}
    state: AppState = app['state']
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
    await send_ws_message(app, MessageType.SYSTEM, data_dict)


def read_ca_telemetry_record(app: web.Application) -> CATelemetryRecord | None:
    state: AppState = app['state']
    if DEV_MODE:
        last_record = state.ca_telemetry_records[-1] if state.ca_telemetry_records else None
        return ca_record_from_random(last_record)
    else:
        if state.ca_serial is not None:
            return ca_record_from_serial(state.ca_serial)


async def ca_telemetry_read_task(app: web.Application):
    telemetry = read_ca_telemetry_record(app)
    state: AppState = app['state']
    if telemetry is not None:
        state.ca_telemetry_records.append(telemetry)


async def ca_telemetry_log_task(app: web.Application):
    state: AppState = app['state']
    last_record = get_last_record(state.ca_telemetry_records, CA_TELEMETRY_READ_INTERVAL)
    if last_record is not None:
        write_to_log(state, last_record)

async def ca_telemetry_websocket_task(app: web.Application):
    state: AppState = app['state']
    last_record = get_last_record(state.ca_telemetry_records, CA_TELEMETRY_READ_INTERVAL)
    if last_record is not None:
        data_dict = last_record.__dict__
        state.log_record_count += 1
        await send_ws_message(app, MessageType.TELEMETRY, data_dict)

async def gnss_task(app: web.Application):
    state: AppState = app['state']
    if DEV_MODE:
        gnss_record = gnss_from_random(state.gnss_records[-1] if state.gnss_records else None)
    if state.gnss_serial is not None:
        gnss_record = gnss_from_serial(state.gnss_serial)
        if gnss_record is not None:
            await send_ws_message(app, MessageType.TELEMETRY, gnss_record.__dict__)

async def electric_telemetry_read_task(app: web.Application):
    state: AppState = app['state']
    if state.ads is not None:
        electric_record_from_ads(state.ads)

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
    if not DEV_MODE:
        create_periodic_task(ping_router, app, name="Router Ping", interval=PING_INTERVAL)
    create_periodic_task(ca_telemetry_read_task, app, name="Cycle Analyst Telemetry", interval=CA_TELEMETRY_READ_INTERVAL)
    create_periodic_task(ca_telemetry_log_task, app, name="Cycle Analyst Log", interval=CA_TELEMETRY_LOG_INTERVAL)
    create_periodic_task(ca_telemetry_websocket_task, app, name="Send CA Telemetry", interval=CA_TELEMETRY_WEBSOCKET_INTERVAL)
    create_periodic_task(gnss_task, app, name="GNSS", interval=GNSS_READ_INTERVAL)
    create_periodic_task(read_system_params, app, name="System Params", interval=SYSTEM_PARAMS_READ_INTERVAL)


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

def init():
    Path(TELEMETRY_LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
    Path(APP_LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
    app = web.Application()
    state = AppState(log_files=get_all_log_files())
    app['state'] = state
    if not DEV_MODE:
        state.ca_serial = get_ca_serial_interface()
        state.ads = get_ads_interface()
    reset_log(state)
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', websocket_handler),
        web.get('/manifest.json', manifest_handler),
        web.get('/logs', log_list_handler),
        web.post('/reset_log', reset_log_handler)
    ])
    for icon_file in FAVICON_FILES:
        app.add_routes([
            web.get(f'/{icon_file}', get_file_serve_handler(f'{FAVICON_DIRECTORY}/{icon_file}'))
        ])
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(on_shutdown)
    return app


def start_server():
    app = init()
    web.run_app(app=app, host='0.0.0.0', port=PORT) # type: ignore


if __name__ == "__main__":
    if DEV_MODE:
        logger.info('Running in development mode. Telemetry will be generated randomly.')
    start_server()
