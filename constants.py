import os
import logging
from typing import Any
from logging import LogRecord

DEV_MODE = os.environ.get('DEV_MODE', 'false').lower() == 'true'
SERVER_PORT = int(os.environ.get('PORT', 8080))

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(SOURCE_DIR, 'public')
SPA_DIST_DIR = os.path.join(SOURCE_DIR, 'spa/dist')
MANIFEST_FILE = os.path.join(SPA_DIST_DIR, 'manifest.json')
JS_FILE = os.path.join(SOURCE_DIR, 'telemetry.js')
STYLES_FILE = os.path.join(SOURCE_DIR, 'spa/src/dash.css')
SPA_HTML_FILE = os.path.join(SPA_DIST_DIR, 'index.html')
SPA_ASSETS_DIR = os.path.join(SPA_DIST_DIR, 'assets')
TELEMETRY_LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'telemetry_logs')
APP_LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'app_logs')
FAVICON_DIRECTORY = os.path.join(SPA_DIST_DIR, 'icons')
JS_DIRECTORY = os.path.join(SOURCE_DIR, 'js')
APP_LOG_FILE = os.path.join(APP_LOG_DIRECTORY, 'app.log')

LOG_VERSION = '1'
LOG_RECORD_COUNT_LIMIT = 36000 # One hour at 10 record/s rate
CA_TELEMETRY_BUFFER_SIZE = 10
SYSTEM_TELEMETRY_BUFFER_SIZE = 10
ELECTRIC_RECORD_BUFFER_SIZE = 10
GNSS_BUFFER_SIZE = 10

# All intervals are in seconds
CA_TELEMETRY_READ_INTERVAL = 0.25
CA_TELEMETRY_LOG_INTERVAL = 0.1
CA_TELEMETRY_SEND_INTERVAL = 0.3
CA_SERIAL_BAUD_RATE = 9600
CA_HARDWARE_SERIAL = os.environ.get('CA_HARDWARE_SERIAL', None)
CA_SOFTWARE_SERIAL_PIN = int(os.environ.get('CA_SOFTWARE_SERIAL_PIN', 4))
ELECTRIC_RECORD_READ_INTERVAL = 0.1
ELECTRIC_RECORD_SEND_INTERVAL = 0.5
GNSS_SERIAL_INTERFACE = os.environ.get('GNSS_SERIAL', '/dev/ttyS0')
GNSS_READ_INTERVAL = 0.5
GNSS_SEND_INTERVAL = 1
GNSS_BAUD_RATE = 115200
SYSTEM_PARAMS_READ_INTERVAL = 0.5
SYSTEM_PARAMS_SEND_INTERVAL = 1
PING_INTERVAL = 5

SERIAL_TIMEOUT = 0.05 # In seconds
WS_TIMEOUT = 0.1 # in seconds
PING_TIMEOUT = 1 # In seconds
ROUTER_HOSTNAME = os.environ.get('ROUTER_HOSTNAME', 'router.grey')

class ColoredFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_template = "%(asctime)s %(message)s"

    FORMATS: dict[int, str] = {
        logging.DEBUG: grey + format_template + reset,
        logging.INFO: blue + format_template + reset,
        logging.WARNING: yellow + format_template + reset,
        logging.ERROR: red + format_template + reset,
        logging.CRITICAL: bold_red + format_template + reset
    }

    def format(self, record: LogRecord):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

LOGGING_CONFIG: dict[str, Any] = {
    'version': 1,
    'formatters': {
        'timestamp': {
            '()': ColoredFormatter,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': APP_LOG_FILE,
            'encoding': 'utf-8',
            'formatter': 'timestamp'
        }
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
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

