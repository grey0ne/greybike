from dataclasses import dataclass, field
from typing import TextIO, TypeVar
from datetime import datetime
from collections import deque
from constants import (
    CA_TELEMETRY_BUFFER_SIZE, GNSS_BUFFER_SIZE, SYSTEM_TELEMETRY_BUFFER_SIZE,
    ELECTRIC_RECORD_BUFFER_SIZE
)
from aiohttp import web
import adafruit_ads1x15.ads1115 as ADS
import asyncio
import os
import random
from serial import Serial


def get_current_timestamp() -> float:
    return datetime.timestamp(datetime.now())


@dataclass(kw_only=True, slots=True, frozen=True)
class BaseRecord:
    """
        Base record class
    """
    timestamp: float = field(default_factory=get_current_timestamp)

@dataclass(kw_only=True, slots=True, frozen=True)
class CATelemetryRecord(BaseRecord):
    """
        Telemetry record from Cycle Analyst V3 serial output
    """
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


@dataclass(kw_only=True, slots=True, frozen=True)
class GNSSRecord(BaseRecord):
    """
        GNSS record from bike onboard receiver. Currently using Holybro Micro m10

        Attributes:
            timestamp (float): Unix timestamp.
            latitude (float): Latitude in minutes.
            longitude (float): Longitude in minutes.
            altitude (float): Altitude above sea level in meters.
            hdop (float): Horizontal Dilution of Precision. Lower is better accuracy.
            sat_num (int): Number of satellites used in fix.
    """
    latitude: float
    longitude: float
    altitude: float | None = None
    speed: float | None = None
    hdop: float | None = None
    sat_num: int | None = None


@dataclass(kw_only=True, slots=True, frozen=True)
class SystemTelemetryRecord(BaseRecord):
    """
        System telemetry record from Raspberry Pi

        Attributes:
            cpu_temp (float): CPU temperature in Celsius.
            memory_usage (float): Memory usage percentage.
            cpu_usage (float): CPU usage percentage.
    """
    cpu_temp: float
    memory_usage: float
    cpu_usage: float


@dataclass(kw_only=True, slots=True, frozen=True)
class ElectricalRecord(BaseRecord):
    """
        Electrical power record for battery and electronics
    """
    current: float
    voltage: float
    timestamp: float = field(default_factory=get_current_timestamp)


@dataclass(kw_only=True, slots=True, frozen=True)
class TaskData:
    """
        Periodic task metadata
    """
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
    ca_serial: Serial | None = None
    gnss_serial: Serial | None = None
    ads: ADS.ADS1115 | None = None
    ca_telemetry_records: deque[CATelemetryRecord] = field(
        default_factory=lambda: deque(maxlen=CA_TELEMETRY_BUFFER_SIZE)
    )
    gnss_records: deque[GNSSRecord] = field(
        default_factory=lambda: deque(maxlen=GNSS_BUFFER_SIZE)
    )
    electric_records: deque[ElectricalRecord] = field(
        default_factory=lambda: deque(maxlen=ELECTRIC_RECORD_BUFFER_SIZE)
    )
    system_telemetry_records: deque[SystemTelemetryRecord] = field(
        default_factory=lambda: deque(maxlen=SYSTEM_TELEMETRY_BUFFER_SIZE)
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

RecordType = TypeVar('RecordType', bound=BaseRecord)

def get_last_record(records: deque[RecordType], interval: float | None = None) -> RecordType | None:
    if len(records) > 0:
        last_record = records[-1]
        if interval is None or last_record.timestamp > datetime.now().timestamp() - interval * 2:
            return last_record

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
