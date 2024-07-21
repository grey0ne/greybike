from dataclasses import dataclass, field
from typing import TextIO
from datetime import datetime
from telemetry import TelemetryRecord
from collections import deque
from constants import TELEMETRY_BUFFER_SIZE
from aiohttp import web
import asyncio
import os
from serial import Serial

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