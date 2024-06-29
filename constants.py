import os

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
JS_FILE = os.path.join(SOURCE_DIR, 'telemetry.js')
LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'logs')

SERIAL_TIMEOUT = 0.1
SERIAL_WAIT_TIME = 0.05
