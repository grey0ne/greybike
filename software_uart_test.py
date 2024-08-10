import sys
import time
import difflib
import pigpio

RX_PIN_NUMBER = 4

SOFTWARE_SERIAL_BAUD_RATE = 9600

def readlines_from_software_uart(interface):
    (count, data) = interface.bb_serial_read(RX_PIN_NUMBER)
    msg = ''
    result = []
    if count:
        for b in data:
            symbol = chr(b)
            if symbol == '\n':
                result.append(msg)
                print(msg)
                msg=''
                continue
            msg += symbol
    return result


def init_software_serial():
    try:
        pi = pigpio.pi()
        pi.set_mode(RX_PIN_NUMBER, pigpio.INPUT)
        pi.bb_serial_read_open(RX_PIN_NUMBER, SOFTWARE_SERIAL_BAUD_RATE, 8)
        return pi
    except Exception as e:
        print(e)
        print("Cannot open software uart")

try:
    interface = init_software_serial()
except Exception as e:
    print(e)
    interface.bb_serial_read_close(RX_PIN_NUMBER)
    interface.stop()

if interface is not None:
    print ("DATA - SOFTWARE SERIAL:")
    try:
        while True:
            lines = readlines_from_software_uart(interface)
            for line in lines:
                print(line)
            time.sleep(0.5)
    except Exception as e:
        print(e)
    finally:
        print('Closing software UART')
        interface.bb_serial_read_close(RX_PIN_NUMBER)
        interface.stop()
