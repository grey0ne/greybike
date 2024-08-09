import './Dash.css';
import { useContext } from 'react';
import { WebSocketContext } from './WebSocketContext';
import { PARAM_OPTIONS } from './types';
import { enumKeys } from './utils';


function ParamContainer({ name, value, unit }: { name: string, value: number, unit: string }) {
    return (
        <div className="param-container">
            <div>
                <span className="param-value">{value}</span>
                <span className="param-unit">{unit}</span>
            </div>
            <div>{name}</div>
        </div>
    )
}

export default function Dash() {
    const socketData = useContext(WebSocketContext);
    const lastTelemetry = socketData?.telemetry[socketData.telemetry.length - 1];
    let paramElems = [];
    if (lastTelemetry) {
        for (const param of enumKeys(lastTelemetry)) {
            const paramData = PARAM_OPTIONS[param];
            paramElems.push(
                <ParamContainer key={param} name={paramData.name} value={lastTelemetry[param]} unit={paramData.unit} />
            )
        }
    }
    return (
        <>
            <div id="telemetry-params">
            </div>
            <div className="row">
                <button id="next-mode-button" className="default-button row-elem">Next Mode</button>
            </div>

            <div style={{width: "100%"}}>
                <canvas id="myChart"></canvas>
            </div>

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
