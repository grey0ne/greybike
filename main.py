from datetime import datetime
from pathlib import Path
from typing import Any
import json
import os
import psutil
import logging
import logging.config
import asyncio
import serial

from aiohttp import web
from serial.serialutil import SerialException

from telemetry import TelemetryRecord, record_from_serial, record_from_random
from constants import (
    TELEMETRY_LOG_DIRECTORY, SERIAL_TIMEOUT, SERIAL_WAIT_TIME,
    SYSTEM_PARAMS_INTERVAL, MANIFEST, APP_LOG_FILE, APP_LOG_DIRECTORY
)
from utils import AppState, apopen
from tasks import create_periodic_task
from logs import write_to_log, reset_log
from dash_page import DASH_PAGE_HTML
from logs_page import render_logs_page

RUNNING_ON_PI = "rpi" in os.uname()[2]
if RUNNING_ON_PI:
    from gpiozero import CPUTemperature # type: ignore
else:
    CPUTemperature = None

PORT = int(os.environ.get('PORT', 8080))
INTERFACE = os.environ.get('SERIAL')
DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'
TELEMETRY_TASK = 'telemetry_task'
ROUTER_HOSTNAME = os.environ.get('ROUTER_HOSTNAME', 'router.grey')
PING_TIMEOUT = 1 # In seconds
PING_INTERVAL = 5 # In seconds

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


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app['websockets'].append(ws)
    try:
        async for msg in ws:
            logger.debug(f'Websocket message {msg}')
            await asyncio.sleep(1)
    finally:
        request.app['websockets'].remove(ws)
    return ws

async def restart_wifi():
    if RUNNING_ON_PI:
        logger.info('Restarting WiFi interface')
        restart_command = 'sudo ip link set wlan0 down && sleep 5 && sudo ip link set wlan0 up'
        await apopen(restart_command)
    else:
        logger.error('Restarting wifi not supported on this platform')

async def ping_router(app: web.Application):
    command = f'ping -c 1 -W{PING_TIMEOUT} {ROUTER_HOSTNAME}'
    ping_result = await apopen(command)
    if ping_result != 0:
        logger.warning(f'{ROUTER_HOSTNAME} ping failed. Return code: {ping_result}')
        await restart_wifi()

async def read_system_params(app: web.Application):
    data_dict: dict[str, float | None] = {}
    state = app['state']
    if CPUTemperature is not None:
        data_dict['cpu_temperature'] = CPUTemperature().temperature
    else:
        data_dict['cpu_temperature'] = None
    data_dict['memory_usage'] = psutil.virtual_memory().percent
    data_dict['cpu_usage'] = psutil.cpu_percent()
    data_dict['log_file'] = state.log_file.name.split('/')[-1]
    data_dict['log_duration'] = (datetime.now() - state.log_start_time).total_seconds()
    data = json.dumps(data_dict)
    for ws in app['websockets']:
        await ws.send_str(data)


async def send_telemetry(app: web.Application, telemetry: TelemetryRecord  | None):
    state = app['state']
    if telemetry is not None:
        data_dict = telemetry.__dict__
        data = json.dumps(data_dict)
        state.log_record_count += 1
        for ws in app['websockets']:
            await ws.send_str(data)

async def read_telemetry(app: web.Application):
    while True:
        telemetry = record_from_serial(app['serial'])
        write_to_log(app['state'], telemetry)
        await send_telemetry(app, telemetry)
        await asyncio.sleep(SERIAL_WAIT_TIME)


async def read_random_telemetry(app: web.Application):
    state = app['state'] 
    telemetry = record_from_random(state.last_telemetry)
    state.last_telemetry = telemetry
    write_to_log(app['state'], telemetry)
    await send_telemetry(app, telemetry)


async def on_shutdown(app: web.Application):
    app['state'].log_file.close()
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')


async def start_background_tasks(app: web.Application):
    state: AppState = app['state']
    if DEV_MODE:
        state.tasks.append(
            create_periodic_task(read_random_telemetry, app, name="Telemetry(Random)", interval=SERIAL_WAIT_TIME)
        )
    else:
        state.tasks.append(
            create_periodic_task(read_telemetry, app, name="Telemetry", interval=SERIAL_WAIT_TIME)
        )
        
    state.tasks.append(create_periodic_task(read_system_params, app, name="System Params", interval=SYSTEM_PARAMS_INTERVAL))
    state.tasks.append(create_periodic_task(ping_router, app, name="Router Ping", interval=PING_INTERVAL))


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
    app['websockets'] = []
    app['state'] = AppState(log_files=get_all_log_files())
    if not DEV_MODE:
        try:
            app['serial'] = serial.Serial(INTERFACE, 9600, timeout=SERIAL_TIMEOUT)
        except SerialException:
            logger.error(f'Could not open serial interface {INTERFACE}')
    reset_log(app['state'])
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', websocket_handler),
        web.get('/manifest.json', manifest_handler),
        web.get('/logs', log_list_handler),
        web.post('/reset_log', reset_log_handler)
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
    else:
        logger.info(f'Using serial interface {INTERFACE}')
    start_server()
