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
                    return [...prevTelemetry, messageData.data];
                });
            }
            if (messageData.type === MessageType.SYSTEM) {
                setSystemRecords((prevSystemState) => {
                    return [...prevSystemState, messageData.data];
                });
            }
            if (messageData.type === MessageType.GNSS) {
                setGnssRecords((prevGnssState) => {
                    return [...prevGnssState, messageData.data]
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

        return;
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