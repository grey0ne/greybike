import { PARAM_OPTIONS, ChartTypeMapping, ChartType, ChartSettings } from './types';
import { LineChart } from '@mui/x-charts/LineChart';
import { useContext } from 'react';
import { WebSocketContext } from './WebSocketContext';
import { Stack, Box } from '@mui/material';

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

export function Chart({ chartType }: { chartType: ChartType }) {
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
            <Stack sx={{ width: 'calc(100% + 40px);', maxWidth: 1000, margin: '0 auto' }}>
                <LineChart
                    { ...chartData }
                    height={300}
                />
            </Stack>
        </Box>
    )
}

