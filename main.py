from datetime import datetime
from pathlib import Path
import json
import os

from aiohttp import web
import asyncio
import serial
from serial.serialutil import SerialException
from dataclasses import dataclass
from typing import TextIO
from gpiozero import CPUTemperature # type: ignore

from telemetry import TelemetryRecord, record_from_serial, record_from_random
from constants import LOG_DIRECTORY, SERIAL_TIMEOUT, SERIAL_WAIT_TIME, MANIFEST
from page import PAGE_TEMPLATE

PORT = int(os.environ.get('PORT', 8080))
INTERFACE = os.environ.get('SERIAL')
DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'
TELEMETRY_TASK = 'telemetry_task'
LOG_VERSION = '1'
LOG_HEADER_TEMPLATE = """
GREYBIKE LOG
VERSION v{version}
FIELDS {fields}
"""
LOG_RECORD_COUNT_LIMIT = 36000 # One hour at 10 record/s rate

LOG_FIELDS = [
    'timestamp', 'speed', 'voltage', 'current', 'trip_distance', 'amper_hours', 'motor_temp',
    'pedal_rpm', 'human_torque', 'human_watts', 'throttle_input', 'throttle_output',
    'mode'
]


@dataclass
class AppState:
    log_file: TextIO | None = None
    log_start_time: datetime | None = None
    log_record_count: int = 0

def print_log(log_str: str):
    # Temporary wrapper to replacer with proper logging later
    print(log_str)

async def http_handler(request: web.Request):
    return web.Response(text=PAGE_TEMPLATE, content_type='text/html')

async def manifest_handler(request: web.Request):
    return web.Response(text=MANIFEST, content_type='application/json')

def reset_log(app: web.Application):
    state = app['state']
    if state.log_file is not None:
        print_log(f'Closing log file {state.log_file.name}')
        state.log_file.close()
    state.log_record_count = 0
    state.log_start_time = datetime.now()
    log_file_path = os.path.join(LOG_DIRECTORY, f'{datetime.now().isoformat()}.log')
    print_log(f'Logging to {log_file_path}')
    state.log_file = open(log_file_path, 'w+')
    log_header = LOG_HEADER_TEMPLATE.format(
        version=LOG_VERSION, fields=','.join(LOG_FIELDS)
    )
    state.log_file.write(log_header)

async def reset_log_handler(request: web.Request):
    reset_log(request.app)
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


async def send_telemetry(app: web.Application, telemetry: TelemetryRecord  | None):
    state = app['state']
    if telemetry is not None:
        if state.log_record_count >= LOG_RECORD_COUNT_LIMIT:
            reset_log(app)
        data_dict = telemetry.__dict__
        data_dict['log_file'] = state.log_file.name.split('/')[-1]
        data_dict['log_duration'] = (datetime.now() - state.log_start_time).total_seconds()
        try:
            data_dict['cpu_temperature'] = CPUTemperature().temperature
        except:
            # Probably running on a non-Raspberry Pi device
            pass
        data = json.dumps(data_dict)
        state.log_record_count += 1
        for ws in app['websockets']:
            await ws.send_str(data)

def write_to_log(app: web.Application, telemetry: TelemetryRecord | None):
    if telemetry is not None:
        data = telemetry.__dict__
        data['timestamp'] = "%.2f" % datetime.timestamp(datetime.now())
        log_record = ','.join(str(data[field]) for field in LOG_FIELDS)
        app['state'].log_file.write(f'{log_record}\n')

async def read_telemetry(app: web.Application):
    try:
        with serial.Serial(INTERFACE, 9600, timeout=SERIAL_TIMEOUT) as ser:
            while True:
                telemetry = record_from_serial(ser)
                write_to_log(app, telemetry)
                await send_telemetry(app, telemetry)
                await asyncio.sleep(SERIAL_WAIT_TIME)
    except SerialException:
        print(f'Could not open serial interface {INTERFACE}')


async def read_random_telemetry(app: web.Application):
    previous = None
    while True:
        telemetry = record_from_random(previous)
        previous = telemetry
        write_to_log(app, telemetry)
        await send_telemetry(app, telemetry)
        await asyncio.sleep(SERIAL_WAIT_TIME)


async def on_shutdown(app: web.Application):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')


async def start_background_tasks(app: web.Application):
    if DEV_MODE:
        app[TELEMETRY_TASK] = asyncio.create_task(read_random_telemetry(app))
    else:
        app[TELEMETRY_TASK] = asyncio.create_task(read_telemetry(app))


async def cleanup_background_tasks(app: web.Application):
    print('cleanup background tasks...')
    app[TELEMETRY_TASK].cancel()
    app['state'].log_file.close()
    await app[TELEMETRY_TASK]


def init():
    app = web.Application()
    app['websockets'] = []
    app['state'] = AppState()
    Path(LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
    reset_log(app)
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', websocket_handler),
        web.get('/manifest.json', manifest_handler),
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
        print('Running in development mode. Telemetry will be generated randomly.')
    else:
        print(f'Using serial interface {INTERFACE}')
    start_server()
