'''
Borrowed from https://github.com/zachary822/asyncio-gpsd-client in order to remove pydantic dependency
'''

import asyncio
import json

from dataclasses import dataclass, asdict
from enum import IntEnum
from datetime import datetime



class Mode(IntEnum):
    unknown = 0
    no_fix = 1
    two_d_fix = 2
    three_d_fix = 3

@dataclass
class Watch:
    enable: bool = True
    split24: bool = False
    raw: int = 0
    json: bool = True


@dataclass
class Version:
    release: str
    rev: str
    proto_major: int
    proto_minor: int

    @property
    def proto(self) -> tuple[int, int]:
        return self.proto_major, self.proto_minor


@dataclass
class Device:
    path: str
    driver: str
    subtype: str
    activated: datetime
    flags: int
    native: int
    bps: int
    parity: str
    stopbits: int
    cycle: float
    mincycle: float


class Devices:
    devices: list[Device]


@dataclass
class TPV:
    device: str
    mode: Mode
    time: datetime
    ept: float
    lat: float
    lon: float
    altHAE: float
    altMSL: float
    alt: float
    magvar: float
    speed: float
    climb: float
    epc: float
    geoidSep: float
    eph: float
    sep: float
    eps: float | None = None
    epx: float | None = None
    epy: float | None = None
    epv: float | None = None
    track: float | None = None
    magtrack: float | None = None


@dataclass
class PRN:
    PRN: int
    el: float
    az: float
    ss: float
    used: bool
    gnssid: int
    svid: int


@dataclass
class Sky:
    device: str
    xdop: float
    ydop: float
    vdop: float
    tdop: float
    hdop: float
    gdop: float
    nSat: int
    uSat: int
    satellites: list[PRN]


@dataclass
class Poll:
    time: datetime
    active: int
    tpv: list[TPV]
    sky: list[Sky]


type Response = Poll | Sky | TPV | list[Device] | Version | Watch

POLL = "?POLL;\r\n"
WATCH = "?WATCH={}\r\n"

class GpsdClientError(Exception):
    pass


class GpsdClient:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    version: Version
    devices: Devices
    watch: Watch
    sky: Sky

    def __init__(self, host: str = "127.0.0.1", port: int = 2947, watch_config: Watch = Watch()):
        self.host = host
        self.port = port

        self.watch_config = watch_config

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        self.writer.write(
            WATCH.format(json.dumps(asdict(self.watch_config))).encode()
        )
        await self.writer.drain()

        self.version = await self.get_result()
        self.devices = await self.get_result()
        self.watch = await self.get_result()

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def get_result(self):
        data = await self.reader.readline()
        data = json.loads(data.decode("utf-8").replace("\r\n", ""))
        print(data)
        result_class = data.get("class")
        del data["class"]
        result = None
        try:
            if result_class == "TPV":
                result = TPV(**data)
            elif result_class == "SKY":
                result = Sky(**data)
        except TypeError as e:
            print(e)
        print(result)
        return result

    async def poll(self):
        self.writer.write(POLL.encode())
        await self.writer.drain()
        return await self.get_result()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self): 
        result = await self.get_result()
        if isinstance(result, TPV):
            return result
        if isinstance(result, Sky):
            self.sky = result
        return await anext(self)
