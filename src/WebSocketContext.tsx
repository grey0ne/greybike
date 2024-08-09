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

    const connection = useRef<any>(null);

    useEffect(() => {
        const ws = new WebSocket(props.wsUrl);
  
        ws.addEventListener("open", () => {
            setIsConnected(true);
            console.log("Websocket connected")
        })
        ws.addEventListener("message", (event) => {
            console.log("Message from server ", event.data)
        })
        ws.addEventListener("error", () => {
            console.error('Socket encountered error. Closing socket');
            connection.current.close();
            setIsConnected(false);
        });

        connection.current = ws;
        return () => connection.current.close()
    }, []);

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