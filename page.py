PARAM_DICT = {
    'amper_hours': {'name': 'Amper Hours', 'unit': 'Ah'},
    'human_torque': {'name': 'Human Torque', 'unit': 'Nm'},
    'human_watts': {'name': 'Human Power', 'unit': 'W'},
    'voltage': {'name': 'Voltage', 'unit': 'V'},
    'current': {'name': 'Current', 'unit': 'A'},
    'rpm': {'name': 'Pedaling RPM', 'unit': ''},
    'speed': {'name': 'Speed', 'unit': 'km/h'},
    'motor_temp': {'name': 'Motor Temp', 'unit': '°C'},
}
PARAM_ELEMS = '\n'.join([f'<div><div><span id="{key}"></span> {param["unit"]}</div><div>{param["name"]}</div></div>' for key, param in PARAM_DICT.items()])

SCRIPT = """
    const socket = new WebSocket("ws://localhost:31337/ws");
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        for (const key in data) {
            const elem = document.getElementById(key)
            if (elem) {
                elem.innerHTML = data[key];
            }
        }
    };
"""

STYLES = """
    .telemetry-params {
        display: flex;
        flex-wrap: wrap;
    }
    .telemetry-params > div {
        width: 30%;
        font-size: 32px;
        text-align: center;
        margin: 10px;
    }
    .telemetry-params span {
        font-size: 48px;
    }
"""

PAGE_TEMPLATE = f"""
<html>
    <head>
        <style>
            {STYLES}
        </style>
        <script>
            {SCRIPT}
        </script>
    </head>
    <body>
        <div class="telemetry-params">
            {PARAM_ELEMS}
        </div>
    </body>
</html>
"""

