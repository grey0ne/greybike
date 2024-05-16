import serial
from aiohttp import web
import asyncio
from dataclasses import dataclass


@dataclass
class TelemetryRecord:
    AH: float
    VOLTAGE: float
    CURRENT: float
    SPEED: float
    DISTANCE: float
    MOTOR_TEMP: float
    RPM: float
    HUMAN_WATTS: float
    HUMAN_TORQUE: float
    THROTTLE_I: float
    THROTTLE_O: float
    AUX_A: float
    AUX_D: float
    FLAGS: str


INTERFACE = '/dev/cu.usbserial-DK0CEN3X'


async def http_handler(request: web.Request):
    return web.Response(text='Greybike telemetry')


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
    with serial.Serial(INTERFACE, 9600, timeout=1) as ser:
        while True:
            await asyncio.sleep(0.1)
            line = ser.readline()
            values = line.decode("utf-8").split("\t")
            if len(values) < 14:
                continue
            telemetry = TelemetryRecord(
                AH=float(values[0]),
                VOLTAGE=float(values[1]),
                CURRENT=float(values[2]),
                SPEED=float(values[3]),
                DISTANCE=float(values[4]),
                MOTOR_TEMP=float(values[5]),
                RPM=float(values[6]),
                HUMAN_WATTS=float(values[7]),
                HUMAN_TORQUE=float(values[8]),
                THROTTLE_I=float(values[9]),
                THROTTLE_O=float(values[10]),
                AUX_A=float(values[11]),
                AUX_D=float(values[12]),
                FLAGS=values[13],
            )

            telemetry_str = f'Ah {telemetry.AH} Voltage {telemetry.VOLTAGE} Current {telemetry.CURRENT} RPM {telemetry.RPM}'
            print(telemetry_str)
            for ws in app['websockets']:
                await ws.send_str(telemetry_str)

TELEMETRY_TASK = 'telemetry_task'

async def on_shutdown(app: web.Application):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')

async def start_background_tasks(app: web.Application):
    app[TELEMETRY_TASK] = app.loop.create_task(read_telemetry(app))


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
    web.run_app(app=app, host='127.0.0.1', port=31337)


if __name__ == "__main__":
    start_server()
