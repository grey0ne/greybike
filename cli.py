import sys
from commands.test_ads import test_ads_sensor
from commands.test_gnss import test_gnss_sensor
from commands.test_log_agregation import test_calculate_log_agregates
from commands.test_software_serial import test_software_serial
from commands.test_ca import test_ca_telemetry
from commands.test_ina228 import test_ina228

COMMANDS = {
    'test_ads': test_ads_sensor,
    'test_gnss': test_gnss_sensor,
    'test_ca': test_ca_telemetry,
    'test_ina228': test_ina228,
    'test_log_agregation': test_calculate_log_agregates,
    'test_software_serial': test_software_serial
}

if len(sys.argv) == 2 and sys.argv[1] in COMMANDS:
    COMMANDS[sys.argv[1]]()
else:
    print('Avaliable commands: ', ' '.join(COMMANDS.keys()))
