import './dash.css';
import { useContext, useState } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import { WebSocketContext } from './WebSocketContext';
import { PARAM_OPTIONS, DashMode, DashModeConfigs, ChartTypeMapping, ChartType, ChartSettings } from './types';
import { Button, Stack, Unstable_Grid2 as Grid, Box } from '@mui/material';
import { enumKeys } from './utils';
import { useWakeLock } from './use-wake-lock';


function ParamContainer({ name, value, unit }: { name: string, value: number, unit: string }) {
    return (
        <Grid xs={6} className="param-container">
            <Stack direction='column' alignItems='center'>
                <div>
                    <span className="param-value">{value.toFixed(2)}</span>
                    &nbsp;
                    <span className="param-unit">{unit}</span>
                </div>
                <div className="param-name">{name}</div>
            </Stack>
        </Grid>
    )
}

function getDataSeries(data: any[], chartSettings: ChartSettings[]): { xAxis: any[], series: any[] } {
    const dataSeries = [];
    const dataLen = data.length;
    const xAxis = data.map((_, i) => dataLen-i);
    for (const chartConf of chartSettings) {
        const param = chartConf.field;
        const paramData = PARAM_OPTIONS[param];
        dataSeries.push({
            label: paramData.name,
            data: data.map((t) => t[param]),
            showMark: false,
            color: chartConf.color
        })
    }
    return { 
        xAxis: [{
            data: xAxis,
            scaleType: 'point',
        }],
        series: dataSeries
    }
}

function Chart({ chartType }: { chartType: ChartType }) {
    let chartData: { xAxis: any[], series: any[] } = { xAxis: [], series: [] };
    const bikeData = useContext(WebSocketContext);
    const chartSettings = ChartTypeMapping[chartType].lines;
    if (chartType === ChartType.power) {
        chartData = getDataSeries(bikeData?.electricRecords || [], chartSettings);
    }
    if (chartType === ChartType.motor || chartType === ChartType.speed) {
        chartData = getDataSeries(bikeData?.telemetry || [], chartSettings);
    }
    return (
        <Box sx={{ width: '100%', overflowX: 'hidden'}}>
            <Stack sx={{ width: 'calc(100% + 40px);', maxWidth: 1000 }}>
                <LineChart
                    { ...chartData }
                    height={300}
                />
            </Stack>
        </Box>
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
        <Grid container direction='row' minHeight='200px' spacing={2} justifyContent='space-around' alignItems='center' width='100%'>
            { paramElems }
        </Grid>
    )
}

export default function Dash() {
    const [mode, setMode] = useState<DashMode>(DashMode.SPEED);
    const [chartType, setChartType] = useState<ChartType>(ChartType.motor);
    const socketData = useContext(WebSocketContext);
    const { type: lockType } = useWakeLock();
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
    const chartButtons = [];
    for (const chartType of enumKeys(ChartType)) {
        const cType = ChartType[chartType];
        chartButtons.push(
            <Button key={cType} variant='contained' onClick={() => setChartType(cType)}>{cType}</Button>
        );
    }
    return (
        <>
            <Stack mt={2} spacing={2} direction='column' alignItems='center' justifyContent='center'>
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
                    { chartButtons }
                </Stack>
                <Stack direction='row' spacing={2}>
                    <Button variant='contained'>Reset Log File</Button>
                    <Button variant='outlined'>All logs</Button>
                </Stack>
            </Stack>
        </>
    )
}
