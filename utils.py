from dataclasses import dataclass, field
from typing import TextIO
from datetime import datetime
from collections import deque
from constants import TELEMETRY_BUFFER_SIZE
from aiohttp import web
import asyncio
import os
import random
from serial import Serial

@dataclass
class CATelemetryRecord:
    """
        Telemetry record from Cycle Analyst V3 serial output
    """
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
    """
        GNSS record from bike onboard receiver. Currently using Holybro Micro m10
    """
    timestamp: float
    latitude: float
    longitude: float
    altitude: float | None = None
    speed: float | None = None

@dataclass
class ElectricalRecord:
    timestamp: float
    current: float
    voltage: float


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
    last_telemetry_records: deque[CATelemetryRecord] = field(
        default_factory=lambda: deque(maxlen=TELEMETRY_BUFFER_SIZE)
    )


def get_random_value(from_: float, to_: float, step:float, previous: float | None) -> float:
    """
        Generate random values for development purposes
    """
    if previous is not None:
        if random.uniform(0, 10) < 1:
            result = previous + random.uniform(-step, step)
            if result < from_:
                result = from_
            elif result > to_:
                result = to_
        else:
            result = previous
    else:
        result = random.uniform(from_, to_)
    return round(result, 2)


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
