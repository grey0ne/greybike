import sys
import time
import difflib
import pigpio
from software_serial import (
    init_software_serial, close_software_serial, readlines_from_software_serial
)

RX_PIN_NUMBER = 4
CA_BAUD_RATE = 9600

interface = init_software_serial(RX_PIN_NUMBER, CA_BAUD_RATE)

if interface is not None:
    print ("DATA - SOFTWARE SERIAL:")
    try:
        while True:
            lines = readlines_from_software_serial(interface)
            for line in lines:
                print(line)
            time.sleep(0.5)
    except Exception as e:
        print(e)
    finally:
        print('Closing software UART')
        close_software_serial(interface)
