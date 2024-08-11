export enum MessageType {
    TELEMETRY = 'telemetry',
    SYSTEM = 'system',
    STATUS = 'status',
    GNSS = 'gnss',
    ELECTRIC = 'electric'
}

export enum DashMode {
    SPEED = 'speed',
    POWER = 'power',
    TEMPERATURE = 'temperature',
    ASSIST = 'assist',
    ODO = 'odo',
    SYSTEM = 'system'
}

export type ParamData = {
    name: string,
    unit: string,
    treshold?: number,
}

enum TelemetryRecordFields {
    amper_hours = 'amper_hours',
    human_torque = 'human_torque',
    human_watts = 'human_watts',
    voltage = 'voltage',
    current = 'current',
}

export type TelemetryRecord = { [key in TelemetryRecordFields]: number }

export type SystemRecord = {
    cpu_temp: number,
    cpu_usage: number,
}

export type GNSSRecord = {
    latitude: number,
    longitude: number,
    altitude: number,
}

export const PARAM_OPTIONS: { [key in TelemetryRecordFields]: ParamData} = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah'},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm', 'treshold': 1},
    'human_watts': {'name': 'Human', 'unit': 'W'},
    'voltage': {'name': 'Voltage', 'unit': 'V'},
    'current': {'name': 'Current', 'unit': 'A'},
}