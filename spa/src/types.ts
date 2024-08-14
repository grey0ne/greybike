import { colors } from '@mui/material';

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
}

export enum TelemetryRecordFields {
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
}

export const DashModeConfigs: { [key in DashMode]: { title: string, fields: TelemetryRecordFields[] } } = {
    'speed': {
        title: 'Speed',
        fields: [TelemetryRecordFields.pedal_rpm, TelemetryRecordFields.speed]
    },
    'power': {
        'title': 'Power',
        'fields': [TelemetryRecordFields.power, TelemetryRecordFields.human_watts, TelemetryRecordFields.regen]
    }
}

export type ParamData = {
    name: string,
    unit: string,
    treshold?: number,
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
    'power': {'name': 'Power', 'unit': 'W'},
    'regen': {'name': 'Regen', 'unit': 'W'},
    'pedal_rpm': {'name': 'Pedal RPM', 'unit': 'rpm'},
    'speed': {'name': 'Speed', 'unit': 'km/h'},
    'timestamp': {'name': 'Time', 'unit': 's'},
}

export enum ChartType {
    power = 'power',
    speed = 'speed',
}

type ChartSettings = {
    field: TelemetryRecordFields,
    color: string
}

export const ChartTypeMapping: { [key in ChartType]: ChartSettings[]} = {
    'power': [
        {'field': TelemetryRecordFields.power, 'color': colors.red[500],},
        {'field': TelemetryRecordFields.human_watts, 'color': colors.blue[500]},
        {'field': TelemetryRecordFields.regen, 'color': colors.green[500]},
    ],
    'speed': [
        {'field': TelemetryRecordFields.pedal_rpm, 'color': colors.red[500]},
        {'field': TelemetryRecordFields.speed, 'color': colors.blue[500]},
    ]
}

