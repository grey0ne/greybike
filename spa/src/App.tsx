import Dash from './Dash'
import { WebSocketProvider } from './WebSocketContext'

function App() {
    return (
        <WebSocketProvider wsUrl={`ws://localhost:8080/ws`}>
            <Dash />
        </WebSocketProvider>
    )
}

export default App
