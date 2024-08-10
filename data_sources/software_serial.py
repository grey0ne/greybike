import pigpio
from dataclasses import dataclass

@dataclass
class SoftwareSerial:
    interface: pigpio.pi
    pin_number: int

def readlines_from_software_serial(serial: SoftwareSerial) -> list[str]:
    (count, data) = serial.interface.bb_serial_read(serial.pin_number)
    msg = ''
    result: list[str] = []
    if count:
        for b in data:
            symbol = chr(int(b))
            if symbol == '\n':
                result.append(msg)
                print(msg)
                msg=''
                continue
            msg += symbol
    return result

def close_software_serial(serial: SoftwareSerial):
    serial.interface.bb_serial_read_close(serial.pin_number)
    serial.interface.stop()

def init_software_serial(pin_number: int, baud_rate: int) -> SoftwareSerial | None:
    pi = None
    try:
        pi = pigpio.pi()
        pi.set_mode(pin_number, pigpio.INPUT)
        pi.bb_serial_read_open(pin_number, baud_rate, 8)
        return SoftwareSerial(
            interface=pi,
            pin_number=pin_number
        )
    except Exception as e:
        print(e)
        print("Cannot open software uart")
        if pi is not None:
            pi.bb_serial_read_close(pin_number)
            pi.stop()
