import { colors } from '@mui/material';

export enum TelemetryType {
    CA = 'ca',
    SYSTEM = 'system',
    STATUS = 'status',
    GNSS = 'gnss',
    ELECTRIC = 'electric'
}

export enum DashMode {
    SPEED = 'speed',
    POWER = 'power',
}

export interface Timestamped {
    timestamp: number
}

export enum CARecordFields {
    timestamp = 'timestamp',
    amper_hours = 'amper_hours',
    human_torque = 'human_torque',
    human_watts = 'human_watts',
    voltage = 'voltage',
    current = 'current',
    power = 'power',
    regen = 'regen',
    pedal_rpm = 'pedal_rpm',
    speed = 'speed',
    motor_temp = 'motor_temp',
}

export const DashModeConfigs: { [key in DashMode]: { title: string, fields: CARecordFields[] } } = {
    'speed': {
        title: 'Speed',
        fields: [CARecordFields.pedal_rpm, CARecordFields.speed]
    },
    'power': {
        'title': 'Power',
        'fields': [CARecordFields.power, CARecordFields.human_watts, CARecordFields.regen]
    }
}

export type ParamData = {
    name: string,
    unit: string,
    treshold?: number,
}


export type TelemetryRecord = { [key in CARecordFields]: number }

export type SystemRecord = {
    cpu_temp: number,
    cpu_usage: number,
}

export type GNSSRecord = {
    timestamp: number,
    latitude: number,
    longitude: number,
    altitude: number,
}

export type ElectricRecord = {
    timestamp: number,
    voltage: number,
    current: number,
    power: number,
    temp: number,
}

type TelemetryFields = CARecordFields | keyof ElectricRecord | keyof SystemRecord | keyof GNSSRecord

export const PARAM_OPTIONS: { [key in TelemetryFields]: ParamData} = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah'},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm', 'treshold': 1},
    'human_watts': {'name': 'Human', 'unit': 'W'},
    'voltage': {'name': 'Voltage', 'unit': 'V'},
    'current': {'name': 'Current', 'unit': 'A'},
    'power': {'name': 'Power', 'unit': 'W'},
    'regen': {'name': 'Regen', 'unit': 'W'},
    'pedal_rpm': {'name': 'Pedal RPM', 'unit': 'rpm'},
    'speed': {'name': 'Speed', 'unit': 'km/h'},
    'timestamp': {'name': 'Time', 'unit': 's'},
    'motor_temp': {'name': 'Motor Temp', 'unit': '°C'},
    'cpu_temp': {'name': 'CPU Temp', 'unit': '°C'},
    'cpu_usage': {'name': 'CPU Usage', 'unit': '%'},
    'temp': {'name': 'Controller Temp', 'unit': '°C'},
    'altitude': {'name': 'Altitude', 'unit': 'm'},
    'latitude': {'name': 'Latitude', 'unit': '°'},
    'longitude': {'name': 'Longitude', 'unit': '°'},
}

export enum ChartType {
    motor = 'motor',
    speed = 'speed',
    power = 'power',
    temp = 'temp',
}

export type ChartSettings = {
    field: TelemetryFields,
    color: string,
    type: TelemetryType
}

type ChartMapping = {
    [key in ChartType]: {
        lines: ChartSettings[]
    }
}

export const ChartTypeMapping: ChartMapping = {
    motor: {
        lines: [
            {field: CARecordFields.power, type: TelemetryType.CA, 'color': colors.red[500],},
            {field: CARecordFields.human_watts, type: TelemetryType.CA, 'color': colors.blue[500]},
            {field: CARecordFields.regen, type: TelemetryType.CA, 'color': colors.green[500]},
        ]
    },
    power: {
        lines: [
            {field: 'power', type: TelemetryType.ELECTRIC, color: colors.green[500]},
        ],
    },
    speed: {
        lines: [
            {field: CARecordFields.pedal_rpm, type: TelemetryType.CA, color: colors.red[500]},
            {field: CARecordFields.speed, type: TelemetryType.CA, color: colors.blue[500]},
        ]
    },
    temp: {
        lines: [
            {field: 'cpu_temp', type: TelemetryType.SYSTEM, color: colors.red[500]},
            {field: 'temp', type: TelemetryType.ELECTRIC, color: colors.green[500]},
            {field: CARecordFields.motor_temp, type: TelemetryType.CA, color: colors.blue[500]},
        ]
    }
}

export type WebSocketData = {
    isConnected: boolean,
    caRecords: TelemetryRecord[],
    systemRecords: SystemRecord[],
    electricRecords: ElectricRecord[],
    gnssRecords: GNSSRecord[]
}