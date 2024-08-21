'''
Borrowed from https://github.com/zachary822/asyncio-gpsd-client in order to remove pydantic dependency
'''

import asyncio
import json

from dataclasses import dataclass, asdict
from enum import IntEnum
from datetime import datetime
from typing import Type
from types import TracebackType
import logging



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
    nmea: bool = False
    scaled: bool = False
    timing: bool = False
    pps: bool = False


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
    activated: datetime
    flags: int
    native: int
    bps: int
    parity: str
    stopbits: int
    cycle: float
    subtype: str | None = None
    mincycle: float | None = None


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
    nSat: int
    uSat: int
    satellites: list[PRN]
    xdop: float | None = None
    ydop: float | None = None
    vdop: float | None = None
    tdop: float | None = None
    hdop: float | None = None
    gdop: float | None = None
    pdop: float | None = None


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
    devices: list[Device]
    watch: Watch
    sky: Sky

    def __init__(self, host: str = "127.0.0.1", port: int = 2947, watch_config: Watch = Watch()):
        self.host = host
        self.port = port

        self.watch_config = watch_config

    async def read_connect_lines(self):
        line_data = await self.get_line_data()
        del line_data['class']
        self.version = Version(**line_data)
        line_data = await self.get_line_data()
        self.devices = []
        for device in line_data['devices']:
            del device['class']
            self.devices.append(Device(**device))
        line_data = await self.get_line_data()
        del line_data['class']
        self.watch = Watch(**line_data)


    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        self.writer.write(
            WATCH.format(json.dumps(asdict(self.watch_config))).encode()
        )
        await self.writer.drain()
        await self.read_connect_lines()

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def get_line_data(self):
        line = await self.reader.readline()
        line = json.loads(line.decode("utf-8").replace("\r\n", ""))
        return line

    async def get_result(self) -> TPV | Sky | None:
        logger = logging.getLogger('greybike')
        data = await self.get_line_data()
        result_class = data.pop("class")
        result = None
        try:
            if result_class == "TPV":
                result = TPV(**data)
            elif result_class == "SKY":
                prns = [PRN(**prn) for prn in data.pop('satellites')]
                data['satellites'] = prns
                result = Sky(**data)
        except TypeError as e:
            logger.debug(e)
        return result

    async def poll(self):
        self.writer.write(POLL.encode())
        await self.writer.drain()
        return await self.get_result()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Type[BaseException], exc: BaseException, tb: TracebackType):
        await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self) -> TPV | Sky | None: 
        result = await self.get_result()
        if isinstance(result, TPV):
            return result
        if isinstance(result, Sky):
            self.sky = result
        return await anext(self)
