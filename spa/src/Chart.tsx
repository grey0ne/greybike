import { PARAM_OPTIONS, ChartTypeMapping, ChartType, ChartSettings, WebSocketData, TelemetryType } from './types';
import { LineChart } from '@mui/x-charts/LineChart';
import { useContext } from 'react';
import { WebSocketContext } from './WebSocketContext';
import { Stack, Box } from '@mui/material';

function getDataSeries(data: WebSocketData, chartSettings: ChartSettings[]): { xAxis: any[], series: any[] } {

    const dataSeries = [];
    let maxLen = 0;
    for (const chartConf of chartSettings) {
        let lineData: any[] = [];
        if (chartConf.type === TelemetryType.SYSTEM) {
            lineData = data.systemRecords;
        } else if (chartConf.type === TelemetryType.CA) {
            lineData = data.caRecords;
        } else if (chartConf.type === TelemetryType.ELECTRIC) {
            lineData = data.electricRecords;
        } else if (chartConf.type === TelemetryType.GNSS) {
            lineData = data.gnssRecords;
        }
        if (lineData.length > maxLen) {
            maxLen = lineData.length;
        }
        const param = chartConf.field;
        const paramData = PARAM_OPTIONS[param];
        dataSeries.push({
            label: paramData.name,
            data: lineData.map((t) => t[param]),
            showMark: false,
            color: chartConf.color
        })
    }
    const xAxis = Array.from({length: maxLen}, (_, i) => maxLen-i)
    return { 
        xAxis: [{
            data: xAxis,
            scaleType: 'point',
        }],
        series: dataSeries
    }
}

export function Chart({ chartType }: { chartType: ChartType }) {
    let chartData: { xAxis: any[], series: any[] } = { xAxis: [], series: [] };
    const bikeData = useContext(WebSocketContext);
    const chartSettings = ChartTypeMapping[chartType].lines;
    if (bikeData !== null) {
        chartData = getDataSeries(bikeData, chartSettings);
    }
    return (
        <Box sx={{ width: '100%', overflowX: 'hidden'}}>
            <Stack sx={{ width: 'calc(100% + 40px);', maxWidth: 1000, margin: '0 auto' }}>
                <LineChart
                    { ...chartData }
                    height={300}
                />
            </Stack>
        </Box>
    )
}

