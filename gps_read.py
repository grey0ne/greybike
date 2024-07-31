import serial
import pynmea2
import os
import io

GNSS_SERIAL_INTERFACE = os.environ.get('GNSS_SERIAL', '/dev/ttyS0')
GNSS_BAUD_RATE = 115200
GNSS_SERIAL_TIMEOUT = 1

ser = serial.Serial(
    port=GNSS_SERIAL_INTERFACE,
    baudrate=GNSS_BAUD_RATE,
    timeout=1
)

for x in range(100):
    try:
        line = ser.readline()
        line = line.decode("utf-8")
        msg = pynmea2.parse(line)
        print(repr(msg))
    except serial.SerialException as e:
        print('Device error: {}'.format(e))
        continue
    except pynmea2.ParseError as e:
        print('Parse error: {}'.format(e))
        continue
