import serial
from aiohttp import web
import asyncio
from dataclasses import dataclass
import json

PORT = 31337
INTERFACE = '/dev/cu.usbserial-DK0CEN3X'
TELEMETRY_TASK = 'telemetry_task'

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

PAGE_TEMPLATE = """
<html>
    <head>
        <script>
            const socket = new WebSocket("ws://localhost:31337/ws");
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                for (const key in data) {
                    const elem = document.getElementById(key)
                    if (elem) {
                        elem.innerHTML = data[key];
                    }
                }
            };
        </script>
    </head>
    <body>
        Grebybike telemetry
        <div>Human Torque <span id="human_torque"></span> Nm</div>
        <div>Voltage <span id="voltage"></span>V</div>
        <div>Pedaling RPM <span id="rpm"></span></div>
        <div>Speed <span id="speed"></span> km/h</div>
    </body>
</html>
"""


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
    with serial.Serial(INTERFACE, 9600, timeout=1) as ser:
        while True:
            await asyncio.sleep(0.1)
            line = ser.readline()
            values = line.decode("utf-8").split("\t")
            if len(values) < 14:
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
            )

            for ws in app['websockets']:
                await ws.send_str(json.dumps(telemetry.__dict__))


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
    web.run_app(app=app, host='127.0.0.1', port=PORT)


if __name__ == "__main__":
    start_server()
