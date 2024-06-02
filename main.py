from datetime import datetime
from pathlib import Path
import json
import os

from aiohttp import web
import asyncio
import serial
from serial.serialutil import SerialException

from telemetry import TelemetryRecord, record_from_serial, record_from_random
from page import PAGE_TEMPLATE

PORT = int(os.environ.get('PORT', 8080))
INTERFACE = os.environ.get('SERIAL')
DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'
TELEMETRY_TASK = 'telemetry_task'
SERIAL_TIMEOUT = 0.1
SERIAL_WAIT_TIME = 0.05
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'logs')


async def http_handler(request: web.Request):
    return web.Response(text=PAGE_TEMPLATE, content_type='text/html')


async def websocket_handler(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app['websockets'].append(ws)
    try:
        async for msg in ws:
            print(f'Websocket message {msg}')
            await asyncio.sleep(1)
    finally:
        request.app['websockets'].remove(ws)
    return ws


async def send_telemetry(app: web.Application, telemetry: TelemetryRecord  | None):
    if telemetry is not None:
        data = json.dumps(telemetry.__dict__)
        for ws in app['websockets']:
            await ws.send_str(data)

def write_to_log(app: web.Application, telemetry: TelemetryRecord | None):
    if telemetry is not None:
        app['log_file'].write(f'{datetime.now().isoformat()} {telemetry.__dict__}\n')

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
    app[TELEMETRY_TASK] = asyncio.create_task(read_random_telemetry(app))


async def cleanup_background_tasks(app: web.Application):
    print('cleanup background tasks...')
    app[TELEMETRY_TASK].cancel()
    app['log_file'].close()
    await app[TELEMETRY_TASK]


def init():
    app = web.Application()
    app['websockets'] = []
    Path(LOG_DIRECTORY).mkdir(parents=True, exist_ok=True)
    log_file = os.path.join(LOG_DIRECTORY, f'{datetime.now().isoformat()}.log')
    print(f'Logging to {log_file}')
    app['log_file'] = open(log_file, 'w+')
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', websocket_handler),
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
