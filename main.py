from dataclasses import dataclass
import json
import os

from aiohttp import web
import serial
import asyncio

from page import PAGE_TEMPLATE

PORT = int(os.environ.get('PORT'))
INTERFACE = os.environ.get('SERIAL')
TELEMETRY_TASK = 'telemetry_task'
SERIAL_TIMEOUT = 0.1
SERIAL_WAIT_TIME = 0.05

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


async def read_telemetry(app: web.Application):
    with serial.Serial(INTERFACE, 9600, timeout=SERIAL_TIMEOUT) as ser:
        while True:
            line = ser.readline()
            values = line.decode("utf-8").split("\t")
            if len(values) < 14:
                await asyncio.sleep(SERIAL_WAIT_TIME)
                continue
            telemetry = TelemetryRecord(
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
                flags=values[13],
                is_brake_pressed=values[13].contains('B')
            )

            data = json.dumps(telemetry.__dict__)
            for ws in app['websockets']:
                await ws.send_str(data)
            await asyncio.sleep(SERIAL_WAIT_TIME)


async def on_shutdown(app: web.Application):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')

async def start_background_tasks(app: web.Application):
    app[TELEMETRY_TASK] = asyncio.create_task(read_telemetry(app))


async def cleanup_background_tasks(app: web.Application):
    print('cleanup background tasks...')
    app[TELEMETRY_TASK].cancel()
    await app[TELEMETRY_TASK]

def init():
    app = web.Application()
    app['websockets'] = []
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
