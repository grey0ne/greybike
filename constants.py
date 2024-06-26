import os

SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(SOURCE_DIR, 'manifest.json')
JS_FILE = os.path.join(SOURCE_DIR, 'telemetry.js')
STYLES_FILE = os.path.join(SOURCE_DIR, 'styles.css')
LOG_DIRECTORY = os.path.join(SOURCE_DIR, 'logs')

SERIAL_TIMEOUT = 0.1
SERIAL_WAIT_TIME = 0.05

with open(JS_FILE) as js_file:
    SCRIPT_CONTENT = js_file.read()

with open(MANIFEST_FILE) as manifest_file:
    MANIFEST = manifest_file.read()

with open(STYLES_FILE) as styles_file:
    STYLES_CONTENT = styles_file.read()