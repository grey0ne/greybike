from dataclasses import dataclass, field
from typing import TextIO
from datetime import datetime

@dataclass
class AppState:
    log_file: TextIO | None = None
    log_start_time: datetime | None = None
    log_record_count: int = 0
    log_files: list[str] = field(default_factory=lambda: [])


def print_log(log_str: str):
    # Temporary wrapper to replacer with proper logging later
    print(log_str)