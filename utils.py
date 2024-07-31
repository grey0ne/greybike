from dataclasses import dataclass, field
from typing import TextIO
from datetime import datetime
from collections import deque
from constants import TELEMETRY_BUFFER_SIZE
from aiohttp import web
import asyncio
import os
from serial import Serial

@dataclass
class TelemetryRecord:
    timestamp: float
    amper_hours: float
    voltage: float
    current: float
    speed: float
    trip_distance: float
    motor_temp: float
    pedal_rpm: float
    human_watts: float
    human_torque: float
    throttle_input: float
    throttle_output: float
    aux_a: float
    aux_d: float
    mode: int
    flags: str
    is_brake_pressed: bool


@dataclass
class GNSSRecord:
    timestamp: float
    latitude: float
    longitude: float
    altitude: float | None = None
    speed: float | None = None


@dataclass
class TaskData:
    name: str
    task: asyncio.Task[None]
    interval: float

@dataclass
class AppState:
    log_file: TextIO | None = None
    log_start_time: datetime | None = None
    log_record_count: int = 0
    log_files: list[str] = field(default_factory=lambda: [])
    tasks: list[TaskData] = field(default_factory=lambda: [])
    websockets: list[web.WebSocketResponse] = field(default_factory=lambda: [])
    serial: Serial | None = None
    last_telemetry_time: datetime | None = None
    last_telemetry_records: deque[TelemetryRecord] = field(
        default_factory=lambda: deque(maxlen=TELEMETRY_BUFFER_SIZE)
    )


async def async_shell(command: str) -> int | None:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()
    return process.returncode

def check_running_on_pi():
    return "rpi" in os.uname()[2]
