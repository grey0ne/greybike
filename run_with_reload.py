import os
import subprocess
import time
import sys
import signal
from typing import Any, Iterable


def is_code(name: str):
    return name.endswith(".py") or name.endswith(".js") or name.endswith(".css")

def end_child_process():
    process.send_signal(signal.SIGINT)

def signal_handler(sig: Any, frame: Any):
    end_child_process()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def file_times(root_path: str) -> Iterable[float]:
    for path in os.listdir(root_path):
        full_path = os.path.join(root_path, path)
        if os.path.isdir(full_path):
            max_times = list(file_times(full_path))
            if len(max_times) > 0:
                yield max(max_times)
        if is_code(full_path):
            yield os.stat(full_path).st_mtime


def print_stdout(process: Any):
    stdout = process.stdout
    if stdout != None:
        print(stdout)


COMMAND = ".venv/bin/python main.py"

# The path to watch
PATH = "."

# How often we check the filesystem for changes (in seconds)
WAIT = 0.5

# The process to autoreload
process = subprocess.Popen(COMMAND, shell=True)

# The current maximum file modified time under the watched directory
last_mtime = max(file_times(PATH))

while True:
    max_mtime = max(file_times(PATH))
    print_stdout(process)
    if max_mtime > last_mtime:
        last_mtime = max_mtime
        print("Restarting process.")
        end_child_process()
        process = subprocess.Popen(COMMAND, shell=True)
    time.sleep(WAIT)
