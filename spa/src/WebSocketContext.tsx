import { createContext, useState, useRef, useEffect, PropsWithChildren } from "react"
import { TelemetryRecord, SystemRecord, TelemetryType, GNSSRecord, ElectricRecord, Timestamped, WebSocketData } from "./types"
import { SetStateAction } from "react"



export const WebSocketContext = createContext<WebSocketData | null>(null)

type WebSocketProviderProps = {
    wsUrl: string
}

const LOGS_DURATION = 200;
const CHART_INTERVAL = 1; // In seconds


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

function processElectricMessage(messageData: any, setElectricRecords: (value: SetStateAction<ElectricRecord[]>) => void) {
    setElectricRecords((prevElectricState: ElectricRecord[]) => {
        const newRecord = messageData.data as ElectricRecord;
        newRecord.power = newRecord.current * newRecord.voltage;
        return rotateElems(prevElectricState, newRecord);
    });
}

export const WebSocketProvider = (props: PropsWithChildren<WebSocketProviderProps>) => {
    const [isConnected, setIsConnected] = useState(false)
    const [caRecords, setCARecords] = useState<TelemetryRecord[]>([])
    const [systemRecords, setSystemRecords] = useState<SystemRecord[]>([]);
    const [gnssRecords, setGnssRecords] = useState<GNSSRecord[]>([]);
    const [electricRecords, setElectricRecords] = useState<ElectricRecord[]>([]);
    const { wsUrl } = props;

    const connection = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!connection.current) {
            connection.current = new WebSocket(wsUrl);
        }
        const ws = connection.current;
  
        ws.addEventListener("open", () => {
            setIsConnected(true);
        })
        ws.addEventListener("message", (event) => {
            const messageData = JSON.parse(event.data);
            if (messageData.type === TelemetryType.CA) {
                proccessTelemetryMessage(messageData, setCARecords);
            }
            if (messageData.type === TelemetryType.SYSTEM) {
                setSystemRecords((prevSystemState) => {
                    return rotateElems(prevSystemState, messageData.data);
                });
            }
            if (messageData.type === TelemetryType.GNSS) {
                setGnssRecords((prevGnssState) => {
                    return rotateElems(prevGnssState, messageData.data);
                })
            }
            if (messageData.type === TelemetryType.ELECTRIC) {
                processElectricMessage(messageData, setElectricRecords);
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
        caRecords: caRecords,
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