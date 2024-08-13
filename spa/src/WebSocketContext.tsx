import { createContext, useState, useRef, useEffect, PropsWithChildren } from "react"
import { TelemetryRecord, SystemRecord, MessageType, GNSSRecord } from "./types"

type WebSocketData = {
    isConnected: boolean,
    telemetry: TelemetryRecord[]
}

export const WebSocketContext = createContext<WebSocketData | null>(null)

type WebSocketProviderProps = {
    wsUrl: string
}
const LOGS_LEN = 40;

function rotateElems<T>(elems: T[], newElem: T): T[] {
    if (elems.length >= LOGS_LEN) {
        elems.splice(0, 1);
    }
    return [...elems, newElem];
}

export const WebSocketProvider = (props: PropsWithChildren<WebSocketProviderProps>) => {
    const [isConnected, setIsConnected] = useState(false)
    const [telemetry, setTelemetry] = useState<TelemetryRecord[]>([])
    const [systemRecords, setSystemRecords] = useState<SystemRecord[]>([]);
    const [gnssRecords, setGnssRecords] = useState<GNSSRecord[]>([]);
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
        gnssRecords: gnssRecords
    }

    return (
        <WebSocketContext.Provider value={ret}>
            {props.children}
        </WebSocketContext.Provider>
    )
}