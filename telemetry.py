from dataclasses import dataclass
import random
import serial


@dataclass
class TelemetryRecord:
    amper_hours: float
    voltage: float
    current: float
    speed: float
    distance: float
    motor_temp: float
    rpm: float
    human_watts: float
    human_torque: float
    throttle_input: float
    throttle_output: float
    aux_a: float
    aux_d: float
    mode: int
    flags: str
    is_brake_pressed: bool

def record_from_values(values: list[str]):
    flags = values[13].replace('\r\n', '')
    return TelemetryRecord(
        amper_hours=float(values[0]),
        voltage=float(values[1]),
        current=float(values[2]),
        speed=float(values[3]),
        distance=float(values[4]),
        motor_temp=float(values[5]),
        rpm=float(values[6]),
        human_watts=float(values[7]),
        human_torque=float(values[8]),
        throttle_input=float(values[9]),
        throttle_output=float(values[10]),
        aux_a=float(values[11]),
        aux_d=float(values[12]),
        flags=flags,
        mode=int(flags[0]),
        is_brake_pressed='B' in flags
    )



def record_from_serial(ser: serial.Serial) -> TelemetryRecord | None:
    line = ser.readline()
    try:
        values = line.decode("utf-8").split("\t")
    except Exception as e:
        print(e)
        return None
    if len(values) < 14:
        return None
    try:
        return record_from_values(values)
    except ValueError:
        return None


def get_random_value(from_: float, to_: float, step:float, previous: float | None) -> float:
    if previous is not None:
        if random.uniform(0, 10) < 1:
            result = previous + random.uniform(-step, step)
            if result < from_:
                result = from_
            elif result > to_:
                result = to_
        else:
            result = previous
    else:
        result = random.uniform(from_, to_)
    return round(result, 2)

def record_from_random(previous: TelemetryRecord | None) -> TelemetryRecord:
    return TelemetryRecord(
        amper_hours=get_random_value(0, 10, 0.01, previous and previous.amper_hours),
        voltage=get_random_value(35, 55, 0.1, previous and previous.voltage),
        current=get_random_value(0, 25, 1, previous and previous.current),
        speed=get_random_value(0, 50, 1, previous and previous.speed),
        distance=get_random_value(0, 100, 0.1, previous and previous.distance),
        motor_temp=get_random_value(20, 80, 0.1, previous and previous.motor_temp),
        rpm=get_random_value(0, 200, 10, previous and previous.rpm),
        human_watts=get_random_value(0, 500, 1, previous and previous.human_watts),
        human_torque=get_random_value(0, 50, 0.1, previous and previous.human_torque),
        throttle_input=get_random_value(0, 100, 0.1, previous and previous.throttle_input),
        throttle_output=get_random_value(0, 100, 0.1, previous and previous.throttle_output),
        aux_a=0,
        aux_d=0,
        flags='',
        mode=1,
        is_brake_pressed=False
 
    )

