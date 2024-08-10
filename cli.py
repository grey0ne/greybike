import sys
from commands.test_ads import test_ads_sensor
from commands.test_gnss import test_gnss_sensor
from commands.test_log_agregation import test_calculate_log_agregates
from commands.test_software_serial import test_software_serial

COMMANDS = {
    'test_ads': test_ads_sensor,
    'test_gnss': test_gnss_sensor,
    'test_log_agregation': test_calculate_log_agregates,
    'test_software_serial': test_software_serial
}

if sys.argv[1] in COMMANDS:
    COMMANDS[sys.argv[1]]()