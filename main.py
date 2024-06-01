from dataclasses import dataclass
from datetime import datetime
import json
import os
import random

from aiohttp import web
import serial
from serial.serialutil import SerialException
import asyncio

from page import PAGE_TEMPLATE

PORT = int(os.environ.get('PORT', 8080))
INTERFACE = os.environ.get('SERIAL')
TELEMETRY_TASK = 'telemetry_task'
SERIAL_TIMEOUT = 0.1
SERIAL_WAIT_TIME = 0.05
LOG_DIRECTORY = 'logs'

@dataclass
class TelemetryRecord:
    amper_hours: float
    voltage: float
    current: float
    speed: float
    distance: float
    motor_temp: float
    rpm: float
    human_watts: float
    human_torque: float
    throttle_input: float
    throttle_output: float
    aux_a: float
    aux_d: float
    mode: int
    flags: str
    is_brake_pressed: bool


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

def record_from_serial(ser: serial.Serial) -> TelemetryRecord | None:
    line = ser.readline()
    values = line.decode("utf-8").split("\t")
    if len(values) < 14:
        return None
    flags = values[13].replace('\r\n', '')
    return TelemetryRecord(
        amper_hours=float(values[0]),
        voltage=float(values[1]),
        current=float(values[2]),
        speed=float(values[3]),
        distance=float(values[4]),
        motor_temp=float(values[5]),
        rpm=float(values[6]),
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

def get_random_value(from_: float, to_: float, step:float, previous: float | None) -> float:
    if previous is not None:
        return previous + random.uniform(-step, step)
    return random.uniform(from_, to_)

def record_from_random(previous: TelemetryRecord | None) -> TelemetryRecord:
    return TelemetryRecord(
        amper_hours=get_random_value(0, 10, 0.01, previous and previous.amper_hours),
        voltage=random.uniform(35, 55),
        current=random.uniform(0, 25),
        speed=random.uniform(0, 50),
        distance=random.uniform(0, 100),
        motor_temp=get_random_value(20, 80, 0.1, previous and previous.motor_temp),
        rpm=get_random_value(0, 200, 1, previous and previous.rpm),
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

async def send_telemetry(app: web.Application, telemetry: TelemetryRecord  | None):
    if telemetry is not None:
        data = json.dumps(telemetry.__dict__)
        for ws in app['websockets']:
            await ws.send_str(data)

async def read_telemetry(app: web.Application):
    try:
        with serial.Serial(INTERFACE, 9600, timeout=SERIAL_TIMEOUT) as ser:
            while True:
                telemetry = record_from_serial(ser)
                await send_telemetry(app, telemetry)
                await asyncio.sleep(SERIAL_WAIT_TIME)
    except SerialException:
        print(f'Could not open serial interface {INTERFACE}')


async def on_shutdown(app: web.Application):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')

async def start_background_tasks(app: web.Application):
    app[TELEMETRY_TASK] = asyncio.create_task(read_telemetry(app))


async def cleanup_background_tasks(app: web.Application):
    print('cleanup background tasks...')
    app[TELEMETRY_TASK].cancel()
    app['log_file'].close()
    await app[TELEMETRY_TASK]


def init():
    app = web.Application()
    app['websockets'] = []
    app['log_file'] = open(os.path.join(LOG_DIRECTORY, f'{datetime.now().isoformat()}.log'), '+w')
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
    print(f'Using serial interface {INTERFACE}')
    start_server()
