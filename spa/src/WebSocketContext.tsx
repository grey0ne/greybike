import { createContext, useState, useRef, useEffect, PropsWithChildren } from "react"
import { TelemetryRecord, SystemRecord, MessageType, GNSSRecord, ElectricRecord } from "./types"
import { SetStateAction } from "react"

type WebSocketData = {
    isConnected: boolean,
    telemetry: TelemetryRecord[],
    systemRecords: SystemRecord[],
    electricRecords: ElectricRecord[],
    gnssRecords: GNSSRecord[]
}

export const WebSocketContext = createContext<WebSocketData | null>(null)

type WebSocketProviderProps = {
    wsUrl: string
}

const LOGS_DURATION = 200;
const CHART_INTERVAL = 1; // In seconds

interface Timestamped {
    timestamp: number
}


function rotateElems<T extends Timestamped>(elems: T[], newElem: T): T[] {
    const lastElem = elems[elems.length - 1];
    if (lastElem && newElem.timestamp - lastElem.timestamp < CHART_INTERVAL) {
        //TODO average values instead of replacing
        newElem.timestamp = lastElem.timestamp;
        elems.splice(-1, 1);
    }
    if (elems.length >= LOGS_DURATION) {
        elems.splice(0, 1);
    }
    return [...elems, newElem];
}

function proccessTelemetryMessage(messageData: any, setTelemetry: (value: SetStateAction<TelemetryRecord[]>) => void) {
    setTelemetry((prevTelemetry: TelemetryRecord[]) => {
        const newRecord = messageData.data as TelemetryRecord;
        const power = newRecord.current * newRecord.voltage;
        if (newRecord.current < 0) {
            newRecord.regen = -power;
            newRecord.power = 0;
        } else {
            newRecord.regen = 0;
            newRecord.power = power;
        }
        return rotateElems(prevTelemetry, newRecord);
    });
}

export const WebSocketProvider = (props: PropsWithChildren<WebSocketProviderProps>) => {
    const [isConnected, setIsConnected] = useState(false)
    const [telemetry, setTelemetry] = useState<TelemetryRecord[]>([])
    const [systemRecords, setSystemRecords] = useState<SystemRecord[]>([]);
    const [gnssRecords, setGnssRecords] = useState<GNSSRecord[]>([]);
    const [electricRecords, setElectricRecords] = useState<ElectricRecord[]>([]);
    const { wsUrl } = props;

    const connection = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!connection.current) {
            console.log("Creating new websocket connection");
            connection.current = new WebSocket(wsUrl);
        }
        const ws = connection.current;
  
        ws.addEventListener("open", () => {
            setIsConnected(true);
        })
        ws.addEventListener("message", (event) => {
            const messageData = JSON.parse(event.data);
            if (messageData.type === MessageType.TELEMETRY) {
                proccessTelemetryMessage(messageData, setTelemetry);
                setTelemetry((prevTelemetry) => {
                    return rotateElems(prevTelemetry, messageData.data);
                });
            }
            if (messageData.type === MessageType.SYSTEM) {
                setSystemRecords((prevSystemState) => {
                    return rotateElems(prevSystemState, messageData.data);
                });
            }
            if (messageData.type === MessageType.GNSS) {
                setGnssRecords((prevGnssState) => {
                    return rotateElems(prevGnssState, messageData.data);
                })
            }
            if (messageData.type === MessageType.ELECTRIC) {
                setElectricRecords((prevElectricState) => {
                    return rotateElems(prevElectricState, messageData.data);
                })
            }
        })
        ws.addEventListener("error", (error) => {
            console.error('Socket encountered error. Closing socket', error);
            if (connection.current) {
                connection.current.close();
            }
            setIsConnected(false);
        });

        return
    }, [wsUrl]);

    const ret = {
        isConnected,
        telemetry: telemetry,
        systemRecords: systemRecords,
        gnssRecords: gnssRecords,
        electricRecords: electricRecords
    }

    return (
        <WebSocketContext.Provider value={ret}>
            {props.children}
        </WebSocketContext.Provider>
    )
}