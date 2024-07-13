import os

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(SOURCE_DIR, 'manifest.json')
JS_FILE = os.path.join(SOURCE_DIR, 'telemetry.js')
STYLES_FILE = os.path.join(SOURCE_DIR, 'styles.css')
LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'logs')

LOG_VERSION = '1'
LOG_RECORD_COUNT_LIMIT = 36000 # One hour at 10 record/s rate

SERIAL_TIMEOUT = 0.1
SERIAL_WAIT_TIME = 0.05
SYSTEM_PARAMS_INTERVAL = 0.5

with open(MANIFEST_FILE) as manifest_file:
    MANIFEST = manifest_file.read()
