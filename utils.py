from typing import TypeVar
from datetime import datetime
from collections import deque
import asyncio
import os
import random
from data_types import BaseRecord



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
