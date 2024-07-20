import os

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(SOURCE_DIR, 'manifest.json')
JS_FILE = os.path.join(SOURCE_DIR, 'telemetry.js')
STYLES_FILE = os.path.join(SOURCE_DIR, 'styles.css')
TELEMETRY_LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'telemetry_logs')
APP_LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'app_logs')
FAVICON_DIRECTORY = os.path.join(SOURCE_DIR, 'icons')
APP_LOG_FILE = os.path.join(APP_LOG_DIRECTORY, 'app.log')

LOG_VERSION = '1'
LOG_RECORD_COUNT_LIMIT = 36000 # One hour at 10 record/s rate
TELEMETRY_BUFFER_SIZE = 10

SERIAL_TIMEOUT = 0.05
SERIAL_WAIT_TIME = 0.09
SERIAL_BAUD_RATE = 9600
SYSTEM_PARAMS_INTERVAL = 0.5

PING_TIMEOUT = 1 # In seconds
PING_INTERVAL = 5 # In seconds
ROUTER_HOSTNAME = os.environ.get('ROUTER_HOSTNAME', 'router.grey')

with open(MANIFEST_FILE) as manifest_file:
    MANIFEST = manifest_file.read()
