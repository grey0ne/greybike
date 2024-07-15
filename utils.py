from dataclasses import dataclass, field
from typing import TextIO
from datetime import datetime
from telemetry import TelemetryRecord
import asyncio

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
    last_telemetry: TelemetryRecord | None = None
    tasks: list[TaskData] = field(default_factory=lambda: [])


async def async_shell(command: str) -> int | None:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()
    return process.returncode

