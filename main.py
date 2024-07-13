from datetime import datetime
from pathlib import Path
import json
import os
import psutil

from aiohttp import web
import asyncio
import serial
from serial.serialutil import SerialException

from telemetry import TelemetryRecord, record_from_serial, record_from_random
from constants import LOG_DIRECTORY, SERIAL_TIMEOUT, SERIAL_WAIT_TIME, MANIFEST
from utils import print_log, AppState
from tasks import create_task
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
            print_log(f'Websocket message {msg}')
            await asyncio.sleep(1)
    finally:
        request.app['websockets'].remove(ws)
    return ws


def read_system_params() -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    if CPUTemperature is not None:
        result['cpu_temperature'] = CPUTemperature().temperature
    else:
        result['cpu_temperature'] = None
    result['memory_usage'] = psutil.virtual_memory().percent
    result['cpu_usage'] = psutil.cpu_percent()
    return result


async def send_telemetry(app: web.Application, telemetry: TelemetryRecord  | None):
    state = app['state']
    if telemetry is not None:
        data_dict = telemetry.__dict__
        data_dict['log_file'] = state.log_file.name.split('/')[-1]
        data_dict['log_duration'] = (datetime.now() - state.log_start_time).total_seconds()
        data_dict.update(read_system_params()) 
        data = json.dumps(data_dict)
        state.log_record_count += 1
        for ws in app['websockets']:
            await ws.send_str(data)

async def read_telemetry(app: web.Application):
    try:
        with serial.Serial(INTERFACE, 9600, timeout=SERIAL_TIMEOUT) as ser:
            while True:
                telemetry = record_from_serial(ser)
                write_to_log(app['state'], telemetry)
                await send_telemetry(app, telemetry)
                await asyncio.sleep(SERIAL_WAIT_TIME)
    except SerialException:
        print_log(f'Could not open serial interface {INTERFACE}')


async def read_random_telemetry(app: web.Application):
    previous = None
    while True:
        telemetry = record_from_random(previous)
        previous = telemetry
        write_to_log(app['state'], telemetry)
        await send_telemetry(app, telemetry)
        await asyncio.sleep(SERIAL_WAIT_TIME)


async def on_shutdown(app: web.Application):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')


async def start_background_tasks(app: web.Application):
    if DEV_MODE:
        app[TELEMETRY_TASK] = create_task(read_random_telemetry(app))
    else:
        app[TELEMETRY_TASK] = create_task(read_telemetry(app))


async def cleanup_background_tasks(app: web.Application):
    print_log('cleanup background tasks...')
    app[TELEMETRY_TASK].cancel()
    app['state'].log_file.close()
    await app[TELEMETRY_TASK]


async def log_list_handler(request: web.Request):
    state = request.app['state']
    return web.Response(text=render_logs_page(state.log_files), content_type='text/html')


def get_all_log_files():
    return os.listdir(LOG_DIRECTORY)

def init():
    app = web.Application()
    app['websockets'] = []
    app['state'] = AppState(log_files=get_all_log_files())
    Path(LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
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
        print_log('Running in development mode. Telemetry will be generated randomly.')
    else:
        print_log(f'Using serial interface {INTERFACE}')
    start_server()
