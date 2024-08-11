import Dash from './Dash'
import { WebSocketProvider } from './WebSocketContext'

function App() {
    return (
        <WebSocketProvider wsUrl={`/ws`}>
            <Dash />
        </WebSocketProvider>
    )
}

export default App
