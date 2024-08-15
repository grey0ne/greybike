import './dash.css';
import { useContext, useState } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import { WebSocketContext } from './WebSocketContext';
import { PARAM_OPTIONS, DashMode, DashModeConfigs, ChartTypeMapping, ChartType } from './types';
import { Button, Stack } from '@mui/material';
import { enumKeys } from './utils';
import { useWakeLock } from './use-wake-lock';


function ParamContainer({ name, value, unit }: { name: string, value: number, unit: string }) {
    return (
        <div className="param-container">
            <div>
                <span className="param-value">{value.toFixed(2)}</span>
                &nbsp;
                <span className="param-unit">{unit}</span>
            </div>
            <div className="param-name">{name}</div>
        </div>
    )
}


function Chart({ chartType }: { chartType: ChartType }) {
    const bikeData = useContext(WebSocketContext);
    const telemetryLen = bikeData?.telemetry.length || 0;
    const xAxis = bikeData?.telemetry.map((_, i) => telemetryLen-i) || [];
    const chartSettings = ChartTypeMapping[chartType];
    const dataSeries = [];
    for  (const chartConf of chartSettings) {
        const param = chartConf.field;
        const paramData = PARAM_OPTIONS[param];
        dataSeries.push({
            label: paramData.name,
            data: bikeData?.telemetry.map((t) => t[param]) || [],
            showMark: false,
            color: chartConf.color
        })
    }
    return (
        <Stack sx={{ width: '100%', maxWidth: 1000 }}>
            <LineChart
                xAxis={[{
                    data: xAxis,
                    scaleType: 'point',
                }]}
                series={dataSeries}
                height={300}
            />
        </Stack>
    )
}


function DashParams({ mode }: { mode: DashMode }){
    const socketData = useContext(WebSocketContext);
    const lastTelemetry = socketData?.telemetry[socketData.telemetry.length - 1];
    const config = DashModeConfigs[mode];
    const paramElems = [];
    if (lastTelemetry) {
        for (const param of config.fields) {
            const paramData = PARAM_OPTIONS[param];
            if (paramData) {
                paramElems.push(
                    <ParamContainer key={param} name={paramData.name} value={lastTelemetry[param]} unit={paramData.unit} />
                )
            }
        }
    }
    return (
        <Stack direction='row' spacing={2} justifyContent='space-around' width='100%'>
            { paramElems }
        </Stack>
    )
}

export default function Dash() {
    const [mode, setMode] = useState<DashMode>(DashMode.SPEED);
    const [chartType, setChartType] = useState<ChartType>(ChartType.power);
    const socketData = useContext(WebSocketContext);
    const { release, type: lockType } = useWakeLock();
    const lastTelemetry = socketData?.telemetry[socketData.telemetry.length - 1];
    const paramElems = [];
    if (lastTelemetry) {
        for (const param of enumKeys(lastTelemetry)) {
            const paramData = PARAM_OPTIONS[param];
            if (paramData) {
                paramElems.push(
                    <ParamContainer key={param} name={paramData.name} value={lastTelemetry[param]} unit={paramData.unit} />
                )
            }
        }
    }
    return (
        <>
            <Stack spacing={2} direction='column' alignItems='center' justifyContent='center'>
                <DashParams mode={mode} />
                <Stack direction='row' spacing={2}>
                    <Button variant='contained' onClick={() => setMode(DashMode.POWER)}>Power</Button>
                    <Button variant='contained' onClick={() => setMode(DashMode.SPEED)}>Speed</Button>
                </Stack>

                <Chart chartType={chartType} />

                <Stack direction='row' spacing={2}>
                    <div>
                        {lockType ? `Wake Lock: ${lockType}` : 'Wake Lock released'}
                    </div>
                    <div>
                        <span id="log_file">
                        </span>
                    </div>
                    <div>
                        <span id="log_duration">
                        </span>
                        &nbsp;Seconds
                    </div>
                </Stack>
                <Stack direction='row' spacing={2}>
                    <Button variant='contained' onClick={() => release()}>Release wake lock</Button>
                    <Button variant='contained' onClick={() => setChartType(ChartType.power)}>Power</Button>
                    <Button variant='contained' onClick={() => setChartType(ChartType.speed)}>Speed</Button>
                </Stack>
                <Stack direction='row' spacing={2}>
                    <Button variant='contained'>Reset Log File</Button>
                    <Button variant='outlined'>All logs</Button>
                </Stack>
            </Stack>
        </>
    )
}
