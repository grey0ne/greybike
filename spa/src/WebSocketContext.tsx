import { createContext, useState, useRef, useEffect, PropsWithChildren } from "react"
import { TelemetryRecord } from "./types"

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
    const { wsUrl } = props;

    const connection = useRef<WebSocket>(null);

    useEffect(() => {
        const ws = new WebSocket(wsUrl);
  
        ws.addEventListener("open", () => {
            setIsConnected(true);
            console.log("Websocket connected")
        })
        ws.addEventListener("message", (event) => {
            setTelemetry((prevTelemetry) => {
                const newTelemetry = JSON.parse(event.data);
                console.log(newTelemetry);
                return [...prevTelemetry ];
            });
        })
        ws.addEventListener("error", (error) => {
            console.error('Socket encountered error: ', error);
            console.error('Socket encountered error. Closing socket');
            if (connection.current) {
                connection.current.close();
            }
            setIsConnected(false);
        });

        return;
    }, [wsUrl]);

    const ret = {
        isConnected,
        telemetry: telemetry
    }

    return (
        <WebSocketContext.Provider value={ret}>
            {props.children}
        </WebSocketContext.Provider>
    )
}