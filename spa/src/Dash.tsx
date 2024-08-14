import './Dash.css';
import { useContext } from 'react';
import { LineChart } from '@mui/x-charts/LineChart';
import { WebSocketContext } from './WebSocketContext';
import { PARAM_OPTIONS, TelemetryRecordFields } from './types';
import { enumKeys } from './utils';
import { colors } from '@mui/material';


function ParamContainer({ name, value, unit }: { name: string, value: number, unit: string }) {
    return (
        <div className="param-container">
            <div>
                <span className="param-value">{value.toFixed(2)}</span>
                &nbsp;
                <span className="param-unit">{unit}</span>
            </div>
            <div>{name}</div>
        </div>
    )
}

enum ChartType {
    power = 'power',
}


type ChartSettings = {
    field: TelemetryRecordFields,
    color: string
}

const ChartTypeMapping: { [key in ChartType]: ChartSettings[]} = {
    'power': [
        {'field': TelemetryRecordFields.power, 'color': colors.red[500],},
        {'field': TelemetryRecordFields.human_watts, 'color': colors.blue[500]},
        {'field': TelemetryRecordFields.regen, 'color': colors.green[500]},
    ]
}


function Chart({ chartType }: { chartType: ChartType }) {
    const bikeData = useContext(WebSocketContext);
    const xAxis = bikeData?.telemetry.map((_, i) => i) || [];
    const chartSettings = ChartTypeMapping[chartType];
    const dataSeries = [];
    for  (const chartConf of chartSettings) {
        dataSeries.push({
            data: bikeData?.telemetry.map((t) => t[chartConf.field]) || [],
            showMark: false,
            color: chartConf.color
        })
    }
    return (
        <div style={{width: "100%"}}>
            <LineChart
                xAxis={[{ data: xAxis }]}
                series={dataSeries}
                width={700}
                height={300}
            />
        </div>
    )
}

export default function Dash() {
    const socketData = useContext(WebSocketContext);
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
            <div id="telemetry-params">
                { paramElems }
            </div>
            <div className="row">
                <button id="next-mode-button" className="default-button row-elem">Next Mode</button>
            </div>

            <Chart chartType={ChartType.power} />

            <div className="row" style={{justifyContent: "space-around"}}>
                <div>
                    <span id="log_file">
                    </span>
                </div>
                <div>
                    <span id="log_duration">
                    </span>
                    &nbsp;Seconds
                </div>
            </div>
            <div className="row">
                <button id="reset-log-button" className="default-button row-elem">Reset log file</button>
            </div>
            <div className="row">
                <a href="/logs" className="default-button row-elem">All Logs</a>
            </div>
        </>
    )
}
