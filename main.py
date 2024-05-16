import serial # nolint

INTERFACE = '/dev/cu.usbserial-DK0CEN3X'

with serial.Serial(INTERFACE, 9600, timeout=1) as ser:
    while True:
        line = ser.readline()
        values = line.decode("utf-8").split("\t")
        if len(values) < 14:
            continue
        AH = values[0]
        VOLTAGE = values[1]
        CURRENT = values[2]
        SPEED = values[3]
        DISTANCE = values[4]
        MOTOR_TEMP = values[5]
        RPM = values[6]
        HUMAN_WATTS = values[7]
        HUMAN_TORQUE = values[8]
        THROTTLE_I = values[9]
        THROTTLE_O = values[10]
        AUX_A = values[11]
        AUX_D = values[12]
        FLAGS = values[13]

        print(f'Ah {AH} Voltage {VOLTAGE} Current {CURRENT} RPM {RPM}')
