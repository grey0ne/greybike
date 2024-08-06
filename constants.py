import os
from typing import Any

DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(SOURCE_DIR, 'manifest.json')
JS_FILE = os.path.join(SOURCE_DIR, 'telemetry.js')
STYLES_FILE = os.path.join(SOURCE_DIR, 'styles.css')
TELEMETRY_LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'telemetry_logs')
APP_LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'app_logs')
FAVICON_DIRECTORY = os.path.join(SOURCE_DIR, 'icons')
JS_DIRECTORY = os.path.join(SOURCE_DIR, 'js')
APP_LOG_FILE = os.path.join(APP_LOG_DIRECTORY, 'app.log')

LOG_VERSION = '1'
LOG_RECORD_COUNT_LIMIT = 36000 # One hour at 10 record/s rate
CA_TELEMETRY_BUFFER_SIZE = 10
SYSTEM_TELEMETRY_BUFFER_SIZE = 10
ELECTRIC_RECORD_BUFFER_SIZE = 10
GNSS_BUFFER_SIZE = 10

SERIAL_TIMEOUT = 0.05 # In seconds
CA_TELEMETRY_READ_INTERVAL = 0.09 # In seconds
CA_TELEMETRY_LOG_INTERVAL = 0.1 # In seconds
CA_TELEMETRY_SEND_INTERVAL = 0.1 # In seconds
ELECTRIC_RECORD_READ_INTERVAL = 0.1 # In seconds
ELECTRIC_RECORD_SEND_INTERVAL = 0.5 # In seconds
GNSS_READ_INTERVAL = 0.5 # In seconds
SYSTEM_PARAMS_READ_INTERVAL = 0.5 # In seconds
SERIAL_BAUD_RATE = 9600

PING_TIMEOUT = 1 # In seconds
PING_INTERVAL = 5 # In seconds
ROUTER_HOSTNAME = os.environ.get('ROUTER_HOSTNAME', 'router.grey')

with open(MANIFEST_FILE) as manifest_file:
    MANIFEST = manifest_file.read()

LOGGING_CONFIG: dict[str, Any] = {
    'version': 1,
    'formatters': {
        'timestamp': {
            'format': '%(asctime)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': APP_LOG_FILE,
            'encoding': 'utf-8',
            'formatter': 'timestamp'
        }
    },
    'loggers': {}
}
if DEV_MODE:
    LOGGING_CONFIG['loggers']['greybike'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }
else:
    LOGGING_CONFIG['loggers']['greybike'] = {
        'level': 'INFO',
        'handlers': ['file']
    }

